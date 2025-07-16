#!/usr/bin/env python3
"""
Script para testar a API de automação do PJe.
"""

import json
import time

import requests


def test_api():
    """Test the PJe automation API."""

    # API configuration
    API_BASE_URL = "http://localhost:8000"

    # Test data
    processo_numero = "5100342-29.2017.8.13.0024"

    print("🧪 Testando API de Automação do PJe")
    print("=" * 50)

    try:
        # Test 1: Health check
        print("\n1️⃣ Testando health check...")
        health_response = requests.get(f"{API_BASE_URL}/api/v1/health")

        if health_response.status_code == 200:
            print("✅ Health check passou!")
            print(f"Response: {health_response.json()}")
        else:
            print(f"❌ Health check falhou: {health_response.status_code}")
            return

        # Test 2: Root endpoint
        print("\n2️⃣ Testando endpoint raiz...")
        root_response = requests.get(f"{API_BASE_URL}/")

        if root_response.status_code == 200:
            print("✅ Root endpoint funcionando!")
            print(f"Response: {root_response.json()}")
        else:
            print(f"❌ Root endpoint falhou: {root_response.status_code}")

        # Test 3: Process download
        print("\n3️⃣ Testando download de processo...")

        payload = {"numero_processo": processo_numero}

        print(f"📤 Enviando requisição para: {API_BASE_URL}/api/v1/baixar-processo")
        print(f"📦 Payload: {json.dumps(payload, indent=2)}")

        download_response = requests.post(
            f"{API_BASE_URL}/api/v1/baixar-processo",
            json=payload,
            headers={"Content-Type": "application/json"},
        )

        if download_response.status_code == 200:
            print("✅ Requisição de download aceita!")
            response_data = download_response.json()
            print(f"📄 Response: {json.dumps(response_data, indent=2)}")

            print("\n⏳ O processo de download foi iniciado em background.")
            print("📋 Verifique os logs da API para acompanhar o progresso.")
            print("🔔 O webhook será chamado quando o download for concluído.")

        else:
            print(f"❌ Requisição de download falhou: {download_response.status_code}")
            print(f"Response: {download_response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão: Certifique-se de que a API está rodando.")
        print("💡 Execute: python app.py")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")


if __name__ == "__main__":
    test_api()
