# PJe TJMG Automation

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Selenium](https://img.shields.io/badge/selenium-4.15.2-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

Uma ferramenta de automação para o sistema PJe (Processo Judicial Eletrônico) do TJMG (Tribunal de Justiça de Minas Gerais).

## 🚀 Funcionalidades

- ✅ **Login Automatizado** - Acesso seguro com credenciais via variáveis de ambiente
- 🔍 **Consulta de Processos** - Busca automatizada por número do processo
- 📄 **Download de Documentos** - Download automático de PDFs dos processos
- 🖼️ **Screenshots de Debug** - Capturas de tela automáticas para debugging
- 📝 **Logging Detalhado** - Sistema de logs estruturado para monitoramento
- 🏗️ **Arquitetura Modular** - Código organizado e reutilizável

## 📁 Estrutura do Projeto

```
pje_project/
├── 📁 src/pje_automation/          # Código principal da aplicação
│   ├── __init__.py                 # Inicialização do pacote
│   ├── pje_client.py              # Cliente principal PJe
│   ├── config.py                  # Configurações centralizadas
│   ├── exceptions.py              # Exceções customizadas
│   └── utils.py                   # Funções utilitárias
├── 📁 tests/                      # Testes automatizados
├── 📁 docs/                       # Documentação adicional
├── 📁 config/                     # Arquivos de configuração
├── 📁 data/                       # PDFs baixados
├── 📁 logs/                       # Arquivos de log
├── 📁 screenshots/                # Screenshots de debug
├── 📁 debug/                      # Arquivos de debug
├── 📁 temp/                       # Arquivos temporários
├── 📁 samples/                    # Exemplos e amostras
├── 📁 venv/                       # Ambiente virtual Python
├── main.py                        # Script principal
├── requirements.txt               # Dependências Python
├── .env                          # Variáveis de ambiente (criar)
├── .gitignore                    # Arquivos ignorados pelo Git
└── README.md                     # Este arquivo
```

## 🛠️ Instalação

### 1. Pré-requisitos

- Python 3.9 ou superior
- Google Chrome instalado
- ChromeDriver (será baixado automaticamente pelo Selenium)

### 2. Clone e Configure

```bash
# Clone o repositório
git clone <repository-url>
cd pje_project

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 3. Configuração de Credenciais

Crie um arquivo `.env` na raiz do projeto:

```bash
# .env
PJE_USERNAME=seu_cpf_ou_cnpj
PJE_PASSWORD=sua_senha
```

## 🎯 Uso

### Uso Básico

```bash
# Executar com interface gráfica
python main.py

# Executar em modo headless (sem interface)
# Edite HEADLESS = True no main.py
```

### Uso Programático

```python
from src.pje_automation import PJeClient

# Usar com context manager (recomendado)
with PJeClient(headless=False, log_level="INFO") as client:
    # Login
    client.login()

    # Navegação
    client.navigate_to_consultation()

    # Busca
    client.search_process("5100342-29.2017.8.13.0024")

    # Download
    file_path = client.download_process_document("5100342-29.2017.8.13.0024")
    print(f"Arquivo baixado: {file_path}")
```

### Configuração Personalizada

```python
from src.pje_automation.config import PJeConfig

# Modificar configurações
PJeConfig.DEFAULT_TIMEOUT = 60
PJeConfig.HEADLESS = True
PJeConfig.DATA_DIR = "meus_downloads"
```

## ⚙️ Configuração

### Variáveis de Ambiente

| Variável | Descrição | Obrigatório |
|----------|-----------|-------------|
| `PJE_USERNAME` | CPF ou CNPJ para login | ✅ |
| `PJE_PASSWORD` | Senha de acesso | ✅ |

### Parâmetros de Configuração

O arquivo `src/pje_automation/config.py` contém todas as configurações:

- **URLs**: Endereços do sistema PJe
- **Timeouts**: Tempos limite para operações
- **Seletores**: Seletores CSS/XPath dos elementos
- **Diretórios**: Caminhos dos arquivos

## 📊 Logging e Debug

### Níveis de Log

- `DEBUG`: Informações detalhadas de debug
- `INFO`: Informações gerais de operação
- `WARNING`: Avisos importantes
- `ERROR`: Erros que impedem a operação

### Arquivos Gerados

- `logs/pje_automation.log`: Log principal da aplicação
- `screenshots/`: Screenshots automáticos durante a execução
- `debug/`: Arquivos HTML e dados de debug
- `data/`: PDFs baixados dos processos

## 🔧 Desenvolvimento

### Executar Testes

```bash
# Executar todos os testes
python -m pytest tests/

# Executar com cobertura
python -m pytest tests/ --cov=src/pje_automation
```

### Estrutura de Classes

```
PJeClient (Cliente Principal)
├── login()                    # Autenticação
├── navigate_to_consultation() # Navegação
├── search_process()           # Busca de processos
└── download_process_document() # Download de documentos

PJeConfig (Configurações)
├── URLs e endpoints
├── Timeouts e limites
├── Seletores CSS/XPath
└── Credenciais

Exceções Customizadas
├── PJeAutomationError        # Erro base
├── LoginError               # Erro de login
├── ProcessNotFoundError     # Processo não encontrado
└── DownloadError           # Erro de download
```

## 🛡️ Segurança

- ✅ Credenciais via variáveis de ambiente
- ✅ Não armazena senhas em código
- ✅ Logs não expõem dados sensíveis
- ✅ Validação de entrada de dados

## 🐛 Solução de Problemas

### Problemas Comuns

1. **ChromeDriver não encontrado**
   ```bash
   # Instalar/atualizar ChromeDriver
   pip install --upgrade selenium
   ```

2. **Elementos não encontrados**
   - Verificar screenshots em `screenshots/`
   - Aumentar timeouts na configuração
   - Verificar seletores CSS

3. **Erro de login**
   - Verificar credenciais no arquivo `.env`
   - Verificar se o site está acessível
   - Verificar logs em `logs/`

### Debug Avançado

```python
# Ativar modo debug
client = PJeClient(log_level="DEBUG")

# Examinar arquivos gerados
# - screenshots/*.png
# - debug/*.html
# - logs/*.log
```

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📞 Suporte

Para suporte e dúvidas:

- 📧 Email: contact@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/user/repo/issues)
- 📖 Documentação: [Wiki](https://github.com/user/repo/wiki)

---

**⚠️ Disclaimer**: Esta ferramenta é para fins educacionais e de automação legítima. Use com responsabilidade e de acordo com os termos de uso do sistema PJe TJMG.
