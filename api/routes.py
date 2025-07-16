"""
API routes for PJe automation.
"""

import asyncio
import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse

from .models import ProcessoRequest, ProcessoResponse
from .services import ProcessoService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/baixar-processo",
    response_model=ProcessoResponse,
    summary="Iniciar download de processo",
    description="Inicia o download assíncrono de um processo do PJe TJMG",
)
async def baixar_processo(
    request: ProcessoRequest, background_tasks: BackgroundTasks
) -> ProcessoResponse:
    """
    Endpoint para iniciar o download de um processo.

    Args:
        request: Dados da requisição contendo o número do processo
        background_tasks: FastAPI background tasks para execução assíncrona

    Returns:
        ProcessoResponse: Resposta indicando que o processo foi iniciado

    Raises:
        HTTPException: Em caso de erro na validação ou processamento inicial
    """
    try:
        numero_processo = request.numero_processo.strip()

        if not numero_processo:
            raise HTTPException(
                status_code=400, detail="Número do processo não pode estar vazio"
            )

        logger.info(f"Recebida requisição para download do processo: {numero_processo}")

        # Add the download task to background tasks
        background_tasks.add_task(ProcessoService.iniciar_download, numero_processo)

        logger.info(f"Task de download iniciada para processo: {numero_processo}")

        return ProcessoResponse(
            status="iniciado",
            numero_processo=numero_processo,
            message=f"Download do processo {numero_processo} foi iniciado",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado no endpoint baixar_processo: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erro interno do servidor: {str(e)}"
        )


@router.get(
    "/health",
    summary="Health check",
    description="Endpoint para verificar se a API está funcionando",
)
async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        content={"status": "healthy", "message": "PJe Automation API está funcionando"}
    )
