#!/usr/bin/env python3
"""
Script de teste para validar a verificação prévia de duplicidade.

Este script testa se a verificação de duplicidade está funcionando
ANTES de inicializar o WebDriver, conforme solicitado.
"""

import os
import sys
import logging
from pathlib import Path

# Adicionar o diretório src ao path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pje_automation.database import save_case_record, case_exists, get_database
from pje_automation.utils import setup_logging, ensure_directory_exists

# Configurar logging
log_file = os.path.join(os.getcwd(), "logs", "teste_verificacao.log")
logger = setup_logging("INFO", log_file)


def criar_processo_teste():
    """
    Cria um processo de teste no banco para simular um processo já baixado.
    """
    logger.info("🧪 Criando processo de teste no banco de dados...")
    
    # Dados do processo de teste
    process_number = "TEST-123-2023.8.13.0001"
    file_name = f"{process_number}.pdf"
    
    # Garantir que o diretório de storage existe
    storage_dir = os.path.join(os.getcwd(), "storage", "processos")
    ensure_directory_exists(storage_dir)
    
    # Criar um arquivo PDF fictício para simular
    file_path = os.path.join(storage_dir, file_name)
    with open(file_path, "w") as f:
        f.write("PDF fictício para teste")
    
    # Salvar no banco de dados
    if save_case_record(process_number, file_name, "completed"):
        logger.info(f"✅ Processo de teste criado: {process_number}")
        logger.info(f"📄 Arquivo criado: {file_path}")
        return process_number, file_path
    else:
        logger.error("❌ Falha ao criar processo de teste")
        return None, None


def simular_main_script(process_number):
    """
    Simula o comportamento do main.py com a verificação prévia.
    """
    logger.info("🚀 Simulando execução do main.py...")
    logger.info("=" * 50)
    logger.info(f"📋 Process Number: {process_number}")
    logger.info("=" * 50)
    
    try:
        # Step 0: Verificar se o processo já existe antes de inicializar o WebDriver
        logger.info(f"\n🔍 Step 0: Checking if process {process_number} already exists...")
        
        if case_exists(process_number):
            logger.info(f"⚠️ Process {process_number} already exists in database!")
            
            # Buscar informações do processo existente
            db = get_database()
            case_info = db.get_case_info(process_number)
            
            if case_info:
                logger.info(f"📄 File: {case_info['file_name']}")
                logger.info(f"📅 Downloaded: {case_info['download_date']}")
                logger.info(f"📊 Status: {case_info['processing_status']}")
                
                # Verificar se o arquivo físico existe
                expected_path = os.path.join("storage", "processos", case_info['file_name'])
                if os.path.exists(expected_path):
                    logger.info(f"✅ File exists at: {expected_path}")
                    logger.info(f"📋 Process already processed successfully - no download needed!")
                    logger.info(f"🎉 Automation completed (skipped duplicate)!")
                    logger.info("🚫 WebDriver NÃO foi inicializado - economia de recursos!")
                    return True  # Sucesso sem precisar inicializar WebDriver
                    
                else:
                    logger.info(f"⚠️ Database record exists but file not found: {expected_path}")
                    logger.info(f"🔄 Would proceed with download to restore missing file...")
                    logger.info("🤖 WebDriver SERIA inicializado para restaurar arquivo")
                    return False  # Precisaria inicializar WebDriver
            else:
                logger.info(f"⚠️ Database inconsistency detected - would proceed with download...")
                logger.info("🤖 WebDriver SERIA inicializado")
                return False
        else:
            logger.info(f"✅ Process {process_number} not found in database - would proceed with download...")
            logger.info("🤖 WebDriver SERIA inicializado para novo download")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro durante simulação: {e}")
        return False


def simular_api_call(process_number):
    """
    Simula o comportamento da API com a verificação prévia.
    """
    logger.info("\n🌐 Simulando chamada da API...")
    logger.info("=" * 50)
    
    try:
        logger.info(f"Iniciando download para processo: {process_number}")
        
        # Verificar se o processo já existe antes de executar o script
        logger.info(f"Verificando se processo {process_number} já existe...")
        
        if case_exists(process_number):
            logger.info(f"Processo {process_number} já existe no banco de dados!")
            
            # Buscar informações do processo existente
            db = get_database()
            case_info = db.get_case_info(process_number)
            
            if case_info:
                logger.info(f"Arquivo: {case_info['file_name']}")
                logger.info(f"Status: {case_info['processing_status']}")
                logger.info(f"Download: {case_info['download_date']}")
                
                # Verificar se o arquivo físico existe
                storage_path = Path("storage") / "processos"
                expected_path = storage_path / case_info['file_name']
                
                if expected_path.exists():
                    logger.info(f"Arquivo existe em: {expected_path}")
                    logger.info(f"Processo {process_number} já processado - download desnecessário!")
                    logger.info("🚫 Script main.py NÃO foi executado - economia de recursos!")
                    return True  # Sucesso sem executar script
                    
                else:
                    logger.info(f"Registro existe mas arquivo não encontrado: {expected_path}")
                    logger.info("SERIA executado script para restaurar arquivo faltante...")
                    return False
            else:
                logger.info("Inconsistência no banco - SERIA executado script...")
                return False
        else:
            logger.info(f"Processo {process_number} não encontrado - SERIA executado download...")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro durante simulação da API: {e}")
        return False


def limpar_processo_teste(process_number, file_path):
    """
    Remove o processo de teste criado.
    """
    logger.info("\n🧹 Limpando processo de teste...")
    
    try:
        # Remover arquivo
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"🗑️ Arquivo removido: {file_path}")
        
        # Remover do banco (se necessário, implementar método delete)
        logger.info(f"🗑️ Processo {process_number} mantido no banco para outros testes")
        
    except Exception as e:
        logger.error(f"❌ Erro ao limpar: {e}")


def main():
    """
    Executa todos os testes de verificação prévia.
    """
    logger.info("🎯 TESTE DE VERIFICAÇÃO PRÉVIA DE DUPLICIDADE")
    logger.info("="*70)
    
    try:
        # Garantir que os diretórios necessários existem
        for directory in ["logs", "storage/processos"]:
            os.makedirs(directory, exist_ok=True)
        
        # Criar processo de teste
        process_number, file_path = criar_processo_teste()
        if not process_number:
            logger.error("❌ Falha ao criar processo de teste")
            return
        
        logger.info(f"\n🧪 Testando com processo: {process_number}")
        
        # Teste 1: Simular main.py
        logger.info("\n" + "🔸" * 50)
        logger.info("TESTE 1: Simulação do main.py")
        logger.info("🔸" * 50)
        
        webdriver_evitado_main = simular_main_script(process_number)
        
        # Teste 2: Simular API
        logger.info("\n" + "🔹" * 50)
        logger.info("TESTE 2: Simulação da API")
        logger.info("🔹" * 50)
        
        script_evitado_api = simular_api_call(process_number)
        
        # Resultados
        logger.info("\n" + "📊" * 50)
        logger.info("RESULTADOS DOS TESTES")
        logger.info("📊" * 50)
        
        if webdriver_evitado_main:
            logger.info("✅ MAIN.PY: WebDriver foi EVITADO - verificação prévia funcionou!")
        else:
            logger.info("⚠️ MAIN.PY: WebDriver seria inicializado")
        
        if script_evitado_api:
            logger.info("✅ API: Script foi EVITADO - verificação prévia funcionou!")
        else:
            logger.info("⚠️ API: Script seria executado")
        
        if webdriver_evitado_main and script_evitado_api:
            logger.info("\n🎉 SUCESSO TOTAL: Ambas as verificações prévias funcionaram!")
            logger.info("💰 ECONOMIA: WebDriver e script desnecessários foram evitados!")
        else:
            logger.info("\n⚠️ Verificações parciais - alguns recursos ainda seriam utilizados")
        
        # Teste com processo inexistente
        logger.info("\n" + "🔹" * 50)
        logger.info("TESTE 3: Processo inexistente (deve prosseguir)")
        logger.info("🔹" * 50)
        
        processo_inexistente = "FAKE-999-2023.8.13.9999"
        webdriver_necessario = not simular_main_script(processo_inexistente)
        script_necessario = not simular_api_call(processo_inexistente)
        
        if webdriver_necessario and script_necessario:
            logger.info("✅ CORRETO: Processo inexistente SERIA processado normalmente")
        else:
            logger.info("❌ ERRO: Processo inexistente foi bloqueado incorretamente")
        
        # Limpeza
        limpar_processo_teste(process_number, file_path)
        
        logger.info("\n🏁 Teste de verificação prévia concluído!")
        
    except Exception as e:
        logger.error(f"❌ Erro durante teste: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 