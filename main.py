#!/usr/bin/env python3
"""
Main entry point for PJe TJMG automation.

This script provides a simple interface to automate login, process search, and document download
from the PJe (Processo Judicial Eletrônico) system of TJMG.
"""

import json
import os
import sys

import requests
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from pje_automation import PJeClient
from pje_automation.database import case_exists, get_database
from pje_automation.exceptions import PJeAutomationError

# Webhook configuration
WEBHOOK_URL = "https://meu-n8n.webhook.com/processo-concluido"
SERVER_BASE_URL = os.getenv("SERVER_BASE_URL", "https://meuservidor.com")


def send_webhook(
    numero_processo: str,
    status: str,
    arquivo_url: str = None,
    arquivo_caminho: str = None,
    erro: str = None,
):
    """
    Send webhook notification after processing.

    Args:
        numero_processo: Process number
        status: Status (sucesso/erro)
        arquivo_url: Public URL of downloaded file
        arquivo_caminho: Local path of downloaded file
        erro: Error message if any
    """
    try:
        payload = {"numero_processo": numero_processo, "status": status}

        if arquivo_url:
            payload["arquivo_url"] = arquivo_url
        if arquivo_caminho:
            payload["arquivo_caminho"] = arquivo_caminho
        if erro:
            payload["erro"] = erro

        print(f"📤 Enviando webhook para: {WEBHOOK_URL}")
        print(f"📦 Payload: {json.dumps(payload, indent=2)}")

        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        if response.status_code == 200:
            print("✅ Webhook enviado com sucesso!")
        else:
            print(f"⚠️ Webhook retornou status {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Erro ao enviar webhook: {e}")


def main():
    """Main function to run PJe automation."""
    # Load environment variables
    load_dotenv()

    # Get process number from command line arguments or use default
    if len(sys.argv) > 1:
        PROCESS_NUMBER = sys.argv[1]
        print(f"📋 Número do processo recebido via argumento: {PROCESS_NUMBER}")
    else:
        PROCESS_NUMBER = "5100342-29.2017.8.13.0024"
        print(f"📋 Usando número do processo padrão: {PROCESS_NUMBER}")

    # Configuration
    HEADLESS = True  # Set to True for API usage
    LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR

    print("🚀 PJe TJMG Automation")
    print("=" * 50)
    print(f"📋 Process Number: {PROCESS_NUMBER}")
    print(f"🖥️  Headless Mode: {HEADLESS}")
    print(f"📝 Log Level: {LOG_LEVEL}")
    print("=" * 50)

    try:
        # Step 0: Verificar se o processo já existe antes de inicializar o WebDriver
        print(f"\n🔍 Step 0: Checking if process {PROCESS_NUMBER} already exists...")
        
        if case_exists(PROCESS_NUMBER):
            print(f"⚠️ Process {PROCESS_NUMBER} already exists in database!")
            
            # Buscar informações do processo existente
            db = get_database()
            case_info = db.get_case_info(PROCESS_NUMBER)
            
            if case_info:
                print(f"📄 File: {case_info['file_name']}")
                print(f"📅 Downloaded: {case_info['download_date']}")
                print(f"📊 Status: {case_info['processing_status']}")
                
                # Verificar se o arquivo físico existe
                expected_path = os.path.join("storage", "processos", case_info['file_name'])
                if os.path.exists(expected_path):
                    print(f"✅ File exists at: {expected_path}")
                    
                    # Gerar URL pública para o arquivo existente
                    arquivo_url = f"{SERVER_BASE_URL}/static/{case_info['file_name']}"
                    
                    # Enviar webhook de sucesso com arquivo existente
                    send_webhook(
                        numero_processo=PROCESS_NUMBER,
                        status="sucesso",
                        arquivo_url=arquivo_url,
                        arquivo_caminho=expected_path,
                    )
                    
                    print(f"📋 Process already processed successfully - no download needed!")
                    print(f"🎉 Automation completed (skipped duplicate)!")
                    return  # Sair sem fazer download
                    
                else:
                    print(f"⚠️ Database record exists but file not found: {expected_path}")
                    print(f"🔄 Will proceed with download to restore missing file...")
            else:
                print(f"⚠️ Database inconsistency detected - proceeding with download...")
        else:
            print(f"✅ Process {PROCESS_NUMBER} not found in database - proceeding with download...")

        # Use context manager for automatic cleanup
        with PJeClient(headless=HEADLESS, log_level=LOG_LEVEL) as client:
            # Step 1: Login
            print("\n🔐 Step 1: Logging in to PJe...")
            client.login()
            print("✅ Login successful!")

            # Step 2: Navigate to consultation
            print("\n🔍 Step 2: Navigating to process consultation...")
            client.navigate_to_consultation()
            print("✅ Navigation successful!")

            # Step 3: Search for process
            print(f"\n🔎 Step 3: Searching for process {PROCESS_NUMBER}...")
            client.search_process(PROCESS_NUMBER)
            print("✅ Search successful!")

            # Step 4: Download document
            print(f"\n⬇️ Step 4: Downloading process document...")
            file_path = client.download_process_document(PROCESS_NUMBER)

            if file_path:
                print(f"✅ Document downloaded successfully!")
                print(f"📄 File saved at: {file_path}")

                # Generate public URL
                filename = os.path.basename(file_path)
                arquivo_url = f"{SERVER_BASE_URL}/static/{filename}"

                # Send success webhook
                send_webhook(
                    numero_processo=PROCESS_NUMBER,
                    status="sucesso",
                    arquivo_url=arquivo_url,
                    arquivo_caminho=file_path,
                )

                print("\n🎉 Automation completed successfully!")
            else:
                error_msg = "Failed to download document"
                print(f"❌ {error_msg}")

                # Send error webhook
                send_webhook(
                    numero_processo=PROCESS_NUMBER, status="erro", erro=error_msg
                )
                sys.exit(1)

    except PJeAutomationError as e:
        error_msg = f"PJe Automation Error: {e}"
        print(f"\n❌ {error_msg}")

        # Send error webhook
        send_webhook(numero_processo=PROCESS_NUMBER, status="erro", erro=error_msg)
        sys.exit(1)

    except KeyboardInterrupt:
        error_msg = "Operation cancelled by user"
        print(f"\n\n⚠️ {error_msg}")

        # Send error webhook
        send_webhook(numero_processo=PROCESS_NUMBER, status="erro", erro=error_msg)
        sys.exit(0)

    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        print(f"\n❌ {error_msg}")

        # Send error webhook
        send_webhook(numero_processo=PROCESS_NUMBER, status="erro", erro=error_msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
