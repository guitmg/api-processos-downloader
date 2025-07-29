#!/usr/bin/env python3
"""
Script de teste para validar a funcionalidade de persistência do banco de dados.

Este script testa todas as funcionalidades principais do módulo de banco de dados
para garantir que a persistência está funcionando corretamente.
"""

import os
import sys
import logging
from pathlib import Path

# Adicionar o diretório src ao path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pje_automation.database import (
    CaseDatabase, 
    save_case_record, 
    case_exists,
    get_database
)

# Configurar logging para o teste
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_database_initialization():
    """Testa a inicialização do banco de dados."""
    logger.info("🧪 Testing database initialization...")
    
    # Usar um banco de teste
    test_db = CaseDatabase("test_case_records.db")
    
    # Verificar se o arquivo foi criado
    assert os.path.exists("test_case_records.db"), "Database file should be created"
    
    logger.info("✅ Database initialization test passed")
    return test_db


def test_case_operations():
    """Testa as operações básicas de casos."""
    logger.info("🧪 Testing case operations...")
    
    test_process = "1234567-89.2023.8.13.0001"
    test_filename = f"{test_process}.pdf"
    
    # Teste 1: Verificar que o caso não existe inicialmente
    assert not case_exists(test_process), "Case should not exist initially"
    logger.info("✅ Case existence check (negative) passed")
    
    # Teste 2: Salvar um novo caso
    assert save_case_record(test_process, test_filename), "Should save new case successfully"
    logger.info("✅ Case save test passed")
    
    # Teste 3: Verificar que o caso agora existe
    assert case_exists(test_process), "Case should exist after saving"
    logger.info("✅ Case existence check (positive) passed")
    
    # Teste 4: Tentar salvar o mesmo caso novamente (deve falhar)
    assert not save_case_record(test_process, test_filename), "Should not save duplicate case"
    logger.info("✅ Duplicate case prevention test passed")
    
    # Teste 5: Buscar informações do caso
    db = get_database()
    case_info = db.get_case_info(test_process)
    assert case_info is not None, "Should retrieve case info"
    assert case_info['case_number'] == test_process, "Case number should match"
    assert case_info['file_name'] == test_filename, "File name should match"
    assert case_info['processing_status'] == "completed", "Status should be completed"
    logger.info("✅ Case info retrieval test passed")


def test_status_update():
    """Testa a atualização de status."""
    logger.info("🧪 Testing status update...")
    
    test_process = "9876543-21.2023.8.13.0002"
    test_filename = f"{test_process}.pdf"
    
    # Salvar um caso com status pending
    save_case_record(test_process, test_filename, "pending")
    
    db = get_database()
    
    # Atualizar status para processing
    assert db.update_processing_status(test_process, "processing"), "Should update status"
    
    # Verificar se foi atualizado
    case_info = db.get_case_info(test_process)
    assert case_info['processing_status'] == "processing", "Status should be updated"
    
    logger.info("✅ Status update test passed")


def test_get_all_cases():
    """Testa a busca de todos os casos."""
    logger.info("🧪 Testing get all cases...")
    
    db = get_database()
    all_cases = db.get_all_cases()
    
    assert isinstance(all_cases, list), "Should return a list"
    assert len(all_cases) >= 2, "Should have at least 2 cases from previous tests"
    
    # Verificar estrutura dos dados
    for case in all_cases:
        assert 'case_number' in case, "Case should have case_number"
        assert 'file_name' in case, "Case should have file_name"
        assert 'download_date' in case, "Case should have download_date"
        assert 'processing_status' in case, "Case should have processing_status"
    
    logger.info(f"✅ Retrieved {len(all_cases)} cases successfully")


def test_validation():
    """Testa as validações de entrada."""
    logger.info("🧪 Testing input validation...")
    
    # Teste com case_number vazio
    assert not save_case_record("", "test.pdf"), "Should reject empty case number"
    assert not save_case_record("   ", "test.pdf"), "Should reject whitespace-only case number"
    
    # Teste com filename vazio
    assert not save_case_record("1234567-89.2023.8.13.0003", ""), "Should reject empty filename"
    assert not save_case_record("1234567-89.2023.8.13.0003", "   "), "Should reject whitespace-only filename"
    
    logger.info("✅ Input validation tests passed")


def cleanup_test_files():
    """Remove arquivos de teste."""
    logger.info("🧹 Cleaning up test files...")
    
    test_files = ["test_case_records.db", "case_records.db"]
    
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            logger.info(f"🗑️ Removed {file}")


def main():
    """Executa todos os testes."""
    logger.info("🚀 Starting database functionality tests...")
    
    try:
        # Limpar arquivos de teste anteriores
        cleanup_test_files()
        
        # Executar testes
        test_database_initialization()
        test_case_operations()
        test_status_update()
        test_get_all_cases()
        test_validation()
        
        logger.info("🎉 All tests passed successfully!")
        
        # Mostrar estatísticas finais
        db = get_database()
        all_cases = db.get_all_cases()
        logger.info(f"📊 Final database contains {len(all_cases)} test cases")
        
        # Mostrar casos salvos
        logger.info("📋 Test cases in database:")
        for case in all_cases:
            logger.info(f"  - {case['case_number']} | {case['file_name']} | {case['processing_status']}")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        sys.exit(1)
    
    finally:
        # Limpar arquivos de teste
        cleanup_test_files()
        logger.info("✅ Test cleanup completed")


if __name__ == "__main__":
    main() 