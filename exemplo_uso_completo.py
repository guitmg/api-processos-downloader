#!/usr/bin/env python3
"""
Exemplo de uso completo do sistema PJe com persistência.

Este script demonstra como usar o PJeClient com a funcionalidade de persistência
para baixar processos judiciais, evitar duplicações e gerenciar metadados.
"""

import os
import sys
import logging
from pathlib import Path

# Adicionar o diretório src ao path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pje_automation.pje_client import PJeClient
from pje_automation.database import get_database, case_exists, save_case_record
from pje_automation.utils import setup_logging

# Configurar logging
log_file = os.path.join(os.getcwd(), "logs", "exemplo_uso.log")
logger = setup_logging("INFO", log_file)


def demonstrar_uso_basico():
    """
    Demonstra o uso básico do sistema com persistência.
    """
    logger.info("🚀 Iniciando demonstração do uso básico do sistema")
    
    # Exemplo de números de processo para teste
    # IMPORTANTE: Substitua por números de processo reais para testar
    processos_exemplo = [
        "1234567-89.2023.8.13.0001",  # Processo fictício para demonstração
        "9876543-21.2023.8.13.0002",  # Processo fictício para demonstração
        "1111111-11.2023.8.13.0003"   # Processo fictício para demonstração
    ]
    
    # Instanciar o banco de dados para verificações
    db = get_database()
    
    logger.info("📋 Verificando processos existentes no banco de dados...")
    
    # Verificar quais processos já existem
    for processo in processos_exemplo:
        if case_exists(processo):
            case_info = db.get_case_info(processo)
            logger.info(f"✅ Processo {processo} já existe no banco")
            logger.info(f"   📄 Arquivo: {case_info['file_name']}")
            logger.info(f"   📅 Download: {case_info['download_date']}")
            logger.info(f"   📊 Status: {case_info['processing_status']}")
        else:
            logger.info(f"🆕 Processo {processo} não encontrado no banco")
    
    logger.info("\n" + "="*60)
    logger.info("💡 EXEMPLO DE USO REAL")
    logger.info("="*60)
    
    # Para demonstrar sem fazer login real (que requer credenciais)
    logger.info("""
    Para usar o sistema completo, você deve:
    
    1. Configurar suas credenciais no arquivo .env:
       - PJE_USERNAME=seu_usuario
       - PJE_PASSWORD=sua_senha
    
    2. Usar o contexto manager do PJeClient:
    
       with PJeClient(headless=True) as client:
           # Login automático com verificação de duplicidade
           client.login()
           
           # Navegar para consulta
           client.navigate_to_consultation()
           
           # Buscar processo
           client.search_process(numero_processo)
           
           # Download com verificação automática de duplicidade
           file_path = client.download_process_document(numero_processo)
           
           if file_path:
               print(f"Arquivo baixado: {file_path}")
           else:
               print("Processo já existe ou erro no download")
    
    3. O sistema automaticamente:
       ✅ Verifica se o processo já foi baixado
       ✅ Salva o PDF com nome {numero_processo}.pdf
       ✅ Armazena em storage/processos/
       ✅ Registra metadados no banco case_records.db
       ✅ Evita downloads duplicados
    """)


def demonstrar_gerenciamento_banco():
    """
    Demonstra as funcionalidades de gerenciamento do banco de dados.
    """
    logger.info("\n" + "="*60)
    logger.info("🗃️ DEMONSTRAÇÃO DO GERENCIAMENTO DO BANCO")
    logger.info("="*60)
    
    db = get_database()
    
    # Adicionar alguns casos de exemplo para demonstração
    casos_exemplo = [
        ("DEMO-001-2023", "DEMO-001-2023.pdf", "completed"),
        ("DEMO-002-2023", "DEMO-002-2023.pdf", "pending"),
        ("DEMO-003-2023", "DEMO-003-2023.pdf", "processing")
    ]
    
    logger.info("📝 Adicionando casos de demonstração...")
    for case_number, filename, status in casos_exemplo:
        if not case_exists(case_number):
            save_case_record(case_number, filename, status)
            logger.info(f"✅ Adicionado: {case_number} ({status})")
        else:
            logger.info(f"⏭️ Já existe: {case_number}")
    
    # Listar todos os casos
    logger.info("\n📋 Todos os casos no banco de dados:")
    all_cases = db.get_all_cases()
    
    if not all_cases:
        logger.info("   (Nenhum caso encontrado)")
    else:
        for case in all_cases:
            logger.info(f"   📄 {case['case_number']}")
            logger.info(f"      Arquivo: {case['file_name']}")
            logger.info(f"      Status: {case['processing_status']}")
            logger.info(f"      Download: {case['download_date']}")
            logger.info("")
    
    # Demonstrar atualização de status
    if all_cases:
        primeiro_caso = all_cases[0]
        case_number = primeiro_caso['case_number']
        novo_status = "completed" if primeiro_caso['processing_status'] != "completed" else "reviewed"
        
        logger.info(f"🔄 Atualizando status do caso {case_number} para '{novo_status}'...")
        if db.update_processing_status(case_number, novo_status):
            logger.info("✅ Status atualizado com sucesso")
        else:
            logger.info("❌ Falha ao atualizar status")


def demonstrar_estrutura_arquivos():
    """
    Demonstra a estrutura de arquivos e diretórios do sistema.
    """
    logger.info("\n" + "="*60)
    logger.info("📂 ESTRUTURA DE ARQUIVOS DO SISTEMA")
    logger.info("="*60)
    
    # Verificar e mostrar estrutura
    estruturas = {
        "Banco de dados": "case_records.db",
        "Diretório de storage": "storage/processos/",
        "Logs": "logs/",
        "Screenshots": "screenshots/",
    }
    
    for nome, caminho in estruturas.items():
        if os.path.exists(caminho):
            if os.path.isfile(caminho):
                size = os.path.getsize(caminho)
                logger.info(f"✅ {nome}: {caminho} ({size} bytes)")
            else:
                files = list(Path(caminho).glob("*"))
                logger.info(f"✅ {nome}: {caminho} ({len(files)} arquivos)")
        else:
            logger.info(f"⚠️ {nome}: {caminho} (não existe)")
    
    # Verificar se há PDFs no diretório de storage
    storage_dir = Path("storage/processos")
    if storage_dir.exists():
        pdf_files = list(storage_dir.glob("*.pdf"))
        logger.info(f"\n📄 PDFs encontrados em storage/processos/: {len(pdf_files)}")
        for pdf in pdf_files[:5]:  # Mostrar apenas os primeiros 5
            size = pdf.stat().st_size
            logger.info(f"   - {pdf.name} ({size} bytes)")
        
        if len(pdf_files) > 5:
            logger.info(f"   ... e mais {len(pdf_files) - 5} arquivos")


def limpar_dados_demonstracao():
    """
    Remove os dados de demonstração criados.
    """
    logger.info("\n" + "="*60)
    logger.info("🧹 LIMPEZA DOS DADOS DE DEMONSTRAÇÃO")
    logger.info("="*60)
    
    # Perguntar se deseja limpar (em um uso real, você pode automatizar isso)
    logger.info("Os dados de demonstração foram criados.")
    logger.info("Para limpar, você pode:")
    logger.info("1. Remover o arquivo case_records.db")
    logger.info("2. Limpar o diretório storage/processos/")
    logger.info("3. Ou usar as funções do banco para remover casos específicos")
    
    # Em um ambiente real, você poderia implementar:
    # db = get_database()
    # for caso in casos_demonstracao:
    #     db.delete_case(caso)


def main():
    """
    Função principal que executa todas as demonstrações.
    """
    logger.info("🎯 SISTEMA PJE COM PERSISTÊNCIA - EXEMPLO COMPLETO")
    logger.info("="*70)
    
    try:
        # Garantir que os diretórios necessários existem
        for directory in ["logs", "storage/processos", "screenshots"]:
            os.makedirs(directory, exist_ok=True)
        
        # Executar demonstrações
        demonstrar_uso_basico()
        demonstrar_gerenciamento_banco()
        demonstrar_estrutura_arquivos()
        limpar_dados_demonstracao()
        
        logger.info("\n🎉 Demonstração concluída com sucesso!")
        logger.info("\nPróximos passos:")
        logger.info("1. Configure suas credenciais no arquivo .env")
        logger.info("2. Use main.py ou a API para baixar processos reais")
        logger.info("3. O sistema gerenciará automaticamente a persistência")
        
    except Exception as e:
        logger.error(f"❌ Erro durante a demonstração: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 