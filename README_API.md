# PJe Automation API

API FastAPI para automação de download de processos do PJe TJMG.

## 🚀 Características

- **Endpoint POST `/api/v1/baixar-processo`**: Inicia download assíncrono de processo
- **Execução assíncrona**: O script roda em background sem bloquear a API
- **Webhook de notificação**: Envia resultado para endpoint configurado
- **Argumentos via linha de comando**: Script aceita número do processo como parâmetro
- **Múltiplas chamadas simultâneas**: Suporta processamento paralelo

## 📋 Estrutura do Projeto

```
pje_project/
├── api/                     # Módulo da API
│   ├── __init__.py
│   ├── config.py           # Configurações
│   ├── models.py           # Modelos Pydantic
│   ├── routes.py           # Rotas da API
│   └── services.py         # Serviços assíncronos
├── app.py                  # Aplicação FastAPI principal
├── main.py                 # Script modificado (aceita argumentos)
├── test_api.py             # Script de teste
└── requirements.txt        # Dependências atualizadas
```

## 🛠️ Instalação e Configuração

### 1. Instalar dependências

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Instalar novas dependências
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente

Crie um arquivo `.env` ou configure:

```bash
# URL base do servidor (para gerar links públicos)
SERVER_BASE_URL=https://meuservidor.com

# Outras configurações existentes do PJe...
```

### 3. Executar a API

```bash
# Opção 1: Usando uvicorn diretamente
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Opção 2: Executando o app.py
python app.py
```

A API estará disponível em: `http://localhost:8000`

## 📡 Endpoints

### POST `/api/v1/baixar-processo`

Inicia o download de um processo.

**Request:**
```json
{
  "numero_processo": "5100342-29.2017.8.13.0024"
}
```

**Response:**
```json
{
  "status": "iniciado",
  "numero_processo": "5100342-29.2017.8.13.0024",
  "message": "Download do processo 5100342-29.2017.8.13.0024 foi iniciado"
}
```

### GET `/api/v1/health`

Health check da API.

**Response:**
```json
{
  "status": "healthy",
  "message": "PJe Automation API está funcionando"
}
```

### GET `/`

Informações da API.

## 🔔 Webhook

Após o download (sucesso ou erro), a API envia um POST para:
```
https://meu-n8n.webhook.com/processo-concluido
```

**Payload de Sucesso:**
```json
{
  "numero_processo": "5100342-29.2017.8.13.0024",
  "status": "sucesso",
  "arquivo_url": "https://meuservidor.com/static/processo_1234567.pdf",
  "arquivo_caminho": "data/processo_1234567.pdf"
}
```

**Payload de Erro:**
```json
{
  "numero_processo": "5100342-29.2017.8.13.0024",
  "status": "erro",
  "erro": "Descrição do erro"
}
```

## 🧪 Testando

### 1. Teste automático

```bash
python test_api.py
```

### 2. Teste manual com curl

```bash
# Health check
curl -X GET http://localhost:8000/api/v1/health

# Download de processo
curl -X POST http://localhost:8000/api/v1/baixar-processo \
  -H "Content-Type: application/json" \
  -d '{"numero_processo": "5100342-29.2017.8.13.0024"}'
```

### 3. Documentação interativa

Acesse: `http://localhost:8000/docs` (Swagger UI)
Ou: `http://localhost:8000/redoc` (ReDoc)

## 🗂️ Arquivos Estáticos

Os arquivos baixados são servidos estaticamente em:
```
http://localhost:8000/static/{filename}
```

## ⚙️ Configurações

### Webhook URL
Configurado em `api/config.py`:
```python
WEBHOOK_URL = "https://meu-n8n.webhook.com/processo-concluido"
```

### Timeouts
- **Script timeout**: 300 segundos (5 minutos)
- **Webhook timeout**: 30 segundos

### Modo Headless
O script agora roda em modo headless por padrão quando chamado pela API.

## 🔄 Fluxo de Funcionamento

1. **Requisição**: Cliente envia POST para `/api/v1/baixar-processo`
2. **Resposta Imediata**: API retorna status "iniciado"
3. **Execução Background**: Script roda assincronamente
4. **Download**: Selenium realiza download do arquivo
5. **Webhook**: API envia resultado para webhook configurado
6. **Arquivo Disponível**: Arquivo acessível via URL estática

## 🚨 Tratamento de Erros

- **Validação**: Pydantic valida entrada
- **Timeout**: Script é terminado após 5 minutos
- **Webhook de Erro**: Notifica falhas via webhook
- **Logs**: Logging detalhado de todas as operações

## 🔒 Considerações de Produção

1. **CORS**: Configure origins apropriados
2. **Autenticação**: Adicione autenticação se necessário
3. **Rate Limiting**: Implemente limitação de taxa
4. **Monitoramento**: Adicione métricas e health checks
5. **SSL**: Use HTTPS em produção
