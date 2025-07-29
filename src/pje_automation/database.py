"""
Módulo de persistência para processos judiciais.

Este módulo gerencia a conexão com o banco de dados SQLite e todas as operações
relacionadas ao armazenamento de metadados dos processos baixados.
"""

import os
import sqlite3
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path


class CaseDatabase:
    """
    Classe para gerenciar o banco de dados de processos judiciais.
    
    Responsável por criar, conectar e gerenciar todas as operações
    do banco SQLite que armazena metadados dos processos.
    """
    
    def __init__(self, db_path: str = "case_records.db"):
        """
        Inicializa a conexão com o banco de dados.
        
        Args:
            db_path: Caminho para o arquivo do banco SQLite
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Garantir que o diretório do banco existe
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        # Criar tabelas se não existirem
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """
        Cria a estrutura inicial do banco de dados.
        
        Cria a tabela 'cases' com todos os campos necessários para
        armazenar informações sobre os processos baixados.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Criar tabela cases se não existir
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS cases (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        case_number TEXT UNIQUE NOT NULL,
                        file_name TEXT NOT NULL,
                        download_date DATETIME NOT NULL,
                        processing_status TEXT DEFAULT 'pending',
                        extracted_text TEXT DEFAULT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Criar índice para melhorar performance de consultas por case_number
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_case_number 
                    ON cases(case_number)
                """)
                
                conn.commit()
                self.logger.info("✅ Database initialized successfully")
                
        except sqlite3.Error as e:
            self.logger.error(f"❌ Error initializing database: {e}")
            raise
    
    def case_exists(self, case_number: str) -> bool:
        """
        Verifica se um processo já está registrado no banco.
        
        Args:
            case_number: Número do processo a verificar
            
        Returns:
            True se o processo já existe, False caso contrário
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM cases WHERE case_number = ?",
                    (case_number,)
                )
                count = cursor.fetchone()[0]
                
                exists = count > 0
                if exists:
                    self.logger.info(f"📋 Process {case_number} already exists in database")
                else:
                    self.logger.info(f"🆕 Process {case_number} not found in database")
                
                return exists
                
        except sqlite3.Error as e:
            self.logger.error(f"❌ Error checking if case exists: {e}")
            return False
    
    def get_case_info(self, case_number: str) -> Optional[Dict[str, Any]]:
        """
        Busca informações de um processo específico.
        
        Args:
            case_number: Número do processo a buscar
            
        Returns:
            Dicionário com informações do processo ou None se não encontrado
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row  # Para retornar como dicionário
                cursor = conn.cursor()
                
                cursor.execute(
                    "SELECT * FROM cases WHERE case_number = ?",
                    (case_number,)
                )
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
                
        except sqlite3.Error as e:
            self.logger.error(f"❌ Error getting case info: {e}")
            return None
    
    def save_case_record(
        self,
        case_number: str,
        file_name: str,
        processing_status: str = "completed"
    ) -> bool:
        """
        Salva um novo registro de processo no banco de dados.
        
        Esta é a função principal para registrar um processo após o download.
        Inclui validações e tratamento de erros adequados.
        
        Args:
            case_number: Número do processo judicial
            file_name: Nome do arquivo PDF salvo
            processing_status: Status do processamento (default: 'completed')
            
        Returns:
            True se salvou com sucesso, False caso contrário
        """
        try:
            # Validar parâmetros de entrada
            if not case_number or not case_number.strip():
                self.logger.error("❌ Case number cannot be empty")
                return False
            
            if not file_name or not file_name.strip():
                self.logger.error("❌ File name cannot be empty")
                return False
            
            # Verificar se o processo já existe
            if self.case_exists(case_number):
                self.logger.warning(f"⚠️ Case {case_number} already exists, skipping save")
                return False
            
            # Salvar no banco de dados
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Data/hora atual para download_date
                download_date = datetime.now().isoformat()
                
                cursor.execute("""
                    INSERT INTO cases (
                        case_number, 
                        file_name, 
                        download_date, 
                        processing_status
                    ) VALUES (?, ?, ?, ?)
                """, (
                    case_number.strip(),
                    file_name.strip(),
                    download_date,
                    processing_status
                ))
                
                conn.commit()
                
                self.logger.info(f"✅ Case {case_number} saved successfully to database")
                self.logger.info(f"📄 File: {file_name}")
                self.logger.info(f"📅 Download date: {download_date}")
                self.logger.info(f"📊 Status: {processing_status}")
                
                return True
                
        except sqlite3.IntegrityError as e:
            self.logger.error(f"❌ Case {case_number} already exists (integrity error): {e}")
            return False
        except sqlite3.Error as e:
            self.logger.error(f"❌ Database error saving case {case_number}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Unexpected error saving case {case_number}: {e}")
            return False
    
    def update_processing_status(
        self, 
        case_number: str, 
        new_status: str
    ) -> bool:
        """
        Atualiza o status de processamento de um processo.
        
        Args:
            case_number: Número do processo
            new_status: Novo status ('pending', 'processing', 'completed', 'error')
            
        Returns:
            True se atualizou com sucesso, False caso contrário
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE cases 
                    SET processing_status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE case_number = ?
                """, (new_status, case_number))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    self.logger.info(f"✅ Status updated for case {case_number}: {new_status}")
                    return True
                else:
                    self.logger.warning(f"⚠️ Case {case_number} not found for status update")
                    return False
                    
        except sqlite3.Error as e:
            self.logger.error(f"❌ Error updating status for case {case_number}: {e}")
            return False
    
    def get_all_cases(self) -> list:
        """
        Busca todos os processos registrados no banco.
        
        Returns:
            Lista de dicionários com informações de todos os processos
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM cases 
                    ORDER BY download_date DESC
                """)
                
                cases = [dict(row) for row in cursor.fetchall()]
                self.logger.info(f"📋 Retrieved {len(cases)} cases from database")
                
                return cases
                
        except sqlite3.Error as e:
            self.logger.error(f"❌ Error retrieving all cases: {e}")
            return []


# Instância global para reutilização
_database_instance = None


def get_database() -> CaseDatabase:
    """
    Retorna uma instância singleton do banco de dados.
    
    Returns:
        Instância única do CaseDatabase
    """
    global _database_instance
    if _database_instance is None:
        _database_instance = CaseDatabase()
    return _database_instance


def save_case_record(
    case_number: str,
    file_name: str,
    processing_status: str = "completed"
) -> bool:
    """
    Função de conveniência para salvar um registro de processo.
    
    Esta é a função principal que deve ser usada pelos outros módulos
    para registrar um processo no banco de dados.
    
    Args:
        case_number: Número do processo judicial
        file_name: Nome do arquivo PDF salvo
        processing_status: Status do processamento (default: 'completed')
        
    Returns:
        True se salvou com sucesso, False caso contrário
    """
    db = get_database()
    return db.save_case_record(case_number, file_name, processing_status)


def case_exists(case_number: str) -> bool:
    """
    Função de conveniência para verificar se um processo existe.
    
    Args:
        case_number: Número do processo a verificar
        
    Returns:
        True se o processo já existe, False caso contrário
    """
    db = get_database()
    return db.case_exists(case_number) 