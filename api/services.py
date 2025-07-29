"""
Services for handling async script execution and webhook notifications.
"""

import asyncio
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import httpx

from .config import settings
from .models import WebhookPayload

# Adicionar path para acessar módulos do projeto
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from pje_automation.database import case_exists, get_database

logger = logging.getLogger(__name__)


class ProcessoService:
    """Service for handling processo downloads."""

    @staticmethod
    async def iniciar_download(numero_processo: str) -> None:
        """
        Start async download process for the given processo number.
        
        Verifica primeiro se o processo já existe antes de executar o script completo.

        Args:
            numero_processo: The process number to download
        """
        try:
            logger.info(f"Iniciando download para processo: {numero_processo}")
            
            # Verificar se o processo já existe antes de executar o script
            logger.info(f"Verificando se processo {numero_processo} já existe...")
            
            if case_exists(numero_processo):
                logger.info(f"Processo {numero_processo} já existe no banco de dados!")
                
                # Buscar informações do processo existente
                db = get_database()
                case_info = db.get_case_info(numero_processo)
                
                if case_info:
                    logger.info(f"Arquivo: {case_info['file_name']}")
                    logger.info(f"Status: {case_info['processing_status']}")
                    logger.info(f"Download: {case_info['download_date']}")
                    
                    # Verificar se o arquivo físico existe
                    storage_path = Path(__file__).parent.parent / "storage" / "processos"
                    expected_path = storage_path / case_info['file_name']
                    
                    if expected_path.exists():
                        logger.info(f"Arquivo existe em: {expected_path}")
                        
                        # Enviar webhook de sucesso para processo já existente
                        await ProcessoService._enviar_webhook_sucesso_existente(
                            numero_processo, str(expected_path), case_info['file_name']
                        )
                        
                        logger.info(f"Processo {numero_processo} já processado - download desnecessário!")
                        return  # Sair sem executar o script
                        
                    else:
                        logger.warning(f"Registro existe mas arquivo não encontrado: {expected_path}")
                        logger.info("Executando script para restaurar arquivo faltante...")
                else:
                    logger.warning("Inconsistência no banco - executando script...")
            else:
                logger.info(f"Processo {numero_processo} não encontrado - executando download...")

            # Execute the script asynchronously
            await ProcessoService._executar_script_async(numero_processo)

        except Exception as e:
            logger.error(
                f"Erro ao iniciar download para processo {numero_processo}: {e}"
            )
            await ProcessoService._enviar_webhook_erro(numero_processo, str(e))

    @staticmethod
    async def _executar_script_async(numero_processo: str) -> None:
        """Execute the main script asynchronously."""
        try:
            # Get the script path relative to project root
            script_path = Path(__file__).parent.parent / settings.SCRIPT_PATH

            # Create the command
            cmd = [sys.executable, str(script_path), numero_processo]

            logger.info(f"Executando comando: {' '.join(cmd)}")

            # Execute subprocess asynchronously
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(script_path.parent),
            )

            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=settings.SCRIPT_TIMEOUT
                )

                if process.returncode == 0:
                    logger.info(
                        f"Script executado com sucesso para processo: {numero_processo}"
                    )
                    await ProcessoService._processar_sucesso(
                        numero_processo, stdout.decode()
                    )
                else:
                    error_msg = (
                        stderr.decode() if stderr else "Script retornou código de erro"
                    )
                    logger.error(
                        f"Script falhou para processo {numero_processo}: {error_msg}"
                    )
                    await ProcessoService._enviar_webhook_erro(
                        numero_processo, error_msg
                    )

            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                error_msg = f"Script timeout após {settings.SCRIPT_TIMEOUT} segundos"
                logger.error(f"Timeout no script para processo {numero_processo}")
                await ProcessoService._enviar_webhook_erro(numero_processo, error_msg)

        except Exception as e:
            logger.error(
                f"Erro na execução do script para processo {numero_processo}: {e}"
            )
            await ProcessoService._enviar_webhook_erro(numero_processo, str(e))

    @staticmethod
    async def _processar_sucesso(numero_processo: str, stdout_output: str) -> None:
        """Process successful script execution and send webhook."""
        try:
            # Try to find the downloaded file path from script output
            arquivo_caminho = ProcessoService._extrair_caminho_arquivo(stdout_output)

            if arquivo_caminho:
                # Generate public URL
                filename = os.path.basename(arquivo_caminho)
                arquivo_url = settings.get_file_url(filename)

                # Send success webhook
                await ProcessoService._enviar_webhook_sucesso(
                    numero_processo, arquivo_url, arquivo_caminho
                )
            else:
                logger.warning(
                    f"Não foi possível encontrar caminho do arquivo para processo {numero_processo}"
                )
                await ProcessoService._enviar_webhook_erro(
                    numero_processo,
                    "Arquivo baixado mas caminho não encontrado no output",
                )

        except Exception as e:
            logger.error(
                f"Erro ao processar sucesso para processo {numero_processo}: {e}"
            )
            await ProcessoService._enviar_webhook_erro(numero_processo, str(e))

    @staticmethod
    def _extrair_caminho_arquivo(stdout_output: str) -> Optional[str]:
        """Extract file path from script stdout output."""
        try:
            # Look for the line that contains "File saved at:"
            lines = stdout_output.split("\n")
            for line in lines:
                if "File saved at:" in line:
                    # Extract the path after "File saved at: "
                    return line.split("File saved at: ")[-1].strip()

            # Alternative: look for data/ path pattern
            for line in lines:
                if "data/" in line and ".pdf" in line:
                    # Extract potential file path
                    parts = line.split()
                    for part in parts:
                        if "data/" in part and ".pdf" in part:
                            return part.strip()

            return None

        except Exception as e:
            logger.error(f"Erro ao extrair caminho do arquivo: {e}")
            return None

    @staticmethod
    async def _enviar_webhook_sucesso_existente(
        numero_processo: str, arquivo_caminho: str, arquivo_nome: str
    ) -> None:
        """
        Enviar webhook de sucesso para processo já existente.
        
        Args:
            numero_processo: Número do processo
            arquivo_caminho: Caminho local do arquivo existente
            arquivo_nome: Nome do arquivo
        """
        try:
            # Gerar URL pública para o arquivo existente
            arquivo_url = settings.get_file_url(arquivo_nome)
            
            payload = WebhookPayload(
                numero_processo=numero_processo,
                status="sucesso",
                arquivo_url=arquivo_url,
                arquivo_caminho=arquivo_caminho,
                message=f"Processo {numero_processo} já processado anteriormente"
            )
            
            logger.info(f"Enviando webhook de sucesso (existente) para {numero_processo}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.WEBHOOK_URL,
                    json=payload.model_dump(),
                    timeout=30.0
                )
                response.raise_for_status()
                logger.info(f"Webhook de sucesso enviado para processo {numero_processo}")
                
        except httpx.HTTPError as e:
            logger.error(f"Erro HTTP ao enviar webhook para {numero_processo}: {e}")
        except Exception as e:
            logger.error(f"Erro inesperado ao enviar webhook para {numero_processo}: {e}")

    @staticmethod
    async def _enviar_webhook_sucesso(
        numero_processo: str, arquivo_url: str, arquivo_caminho: str
    ) -> None:
        """Send success webhook notification."""
        payload = WebhookPayload(
            numero_processo=numero_processo,
            status="sucesso",
            arquivo_url=arquivo_url,
            arquivo_caminho=arquivo_caminho,
        )

        await ProcessoService._enviar_webhook(payload)

    @staticmethod
    async def _enviar_webhook_erro(numero_processo: str, erro: str) -> None:
        """Send error webhook notification."""
        payload = WebhookPayload(
            numero_processo=numero_processo, status="erro", erro=erro
        )

        await ProcessoService._enviar_webhook(payload)

    @staticmethod
    async def _enviar_webhook(payload: WebhookPayload) -> None:
        """Send webhook notification."""
        try:
            async with httpx.AsyncClient(timeout=settings.WEBHOOK_TIMEOUT) as client:
                response = await client.post(
                    settings.WEBHOOK_URL,
                    json=payload.model_dump(),
                    headers={"Content-Type": "application/json"},
                )

                if response.status_code == 200:
                    logger.info(
                        f"Webhook enviado com sucesso para processo: {payload.numero_processo}"
                    )
                else:
                    logger.warning(
                        f"Webhook retornou status {response.status_code} para processo: {payload.numero_processo}"
                    )

        except Exception as e:
            logger.error(
                f"Erro ao enviar webhook para processo {payload.numero_processo}: {e}"
            )
