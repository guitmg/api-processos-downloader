# Estrutura Organizada do Projeto PJe TJMG Automation

## 📁 Estrutura Final

```
pje_project/
├── 📁 src/pje_automation/          # 🏗️ Código principal da aplicação
│   ├── __init__.py                 # Inicialização do pacote
│   ├── pje_client.py              # Cliente principal PJe (classe refatorada)
│   ├── config.py                  # Configurações centralizadas
│   ├── exceptions.py              # Exceções customizadas
│   └── utils.py                   # Funções utilitárias
│
├── 📁 tests/                      # 🧪 Testes automatizados
│   ├── __init__.py                # Inicialização do pacote de testes
│   └── test_utils.py              # Testes das funções utilitárias
│
├── 📁 docs/                       # 📚 Documentação adicional
├── 📁 config/                     # ⚙️ Arquivos de configuração
├── 📁 data/                       # 📄 PDFs baixados
│   └── 5100342-29.2017.8.13.0024-processo.pdf
├── 📁 logs/                       # 📝 Arquivos de log
│   └── pje_automation.log
├── 📁 screenshots/                # 📸 Screenshots de debug
│   ├── 01_main_page.png
│   ├── 02_iframe_content.png
│   ├── 03_before_submit.png
│   ├── 04_after_refresh.png
│   ├── 05_consultation_page.png
│   ├── 06_fields_filled.png
│   ├── 07_search_results.png
│   ├── 08_process_details.png
│   ├── 09_dropdown_opened.png
│   ├── 10_download_initiated.png
│   └── 11_pdf_tab.png
├── 📁 debug/                      # 🔍 Arquivos de debug
│   ├── debug_download_page.html
│   ├── debug_pje_html.py
│   ├── iframe_0_html.txt
│   ├── input_fields_debug.txt
│   ├── pje_html_delayed.txt
│   └── pje_html_immediate.txt
├── 📁 temp/                       # 🗂️ Arquivos temporários
│   └── pje_login.py              # Script original (backup)
├── 📁 samples/                    # 💼 Exemplos e amostras
├── 📁 venv/                       # 🐍 Ambiente virtual Python
│
├── main.py                        # 🚀 Script principal de execução
├── setup.py                       # 📦 Configuração para instalação
├── requirements.txt               # 📋 Dependências Python
├── .env                          # 🔐 Variáveis de ambiente
├── .gitignore                    # 🚫 Arquivos ignorados pelo Git
├── README.md                     # 📖 Documentação principal
└── STRUCTURE.md                  # 📁 Este arquivo
```

## 🔄 Migração Realizada

### Antes (Estrutura Monolítica)
- ❌ Código em um único arquivo `pje_login.py` (1000+ linhas)
- ❌ Arquivos espalhados na raiz do projeto
- ❌ Configurações hardcoded no código
- ❌ Sem separação de responsabilidades
- ❌ Difícil manutenção e testing

### Depois (Estrutura Modular)
- ✅ **Código modularizado** em múltiplos arquivos especializados
- ✅ **Configurações centralizadas** em `config.py`
- ✅ **Exceções customizadas** para melhor tratamento de erros
- ✅ **Utilitários separados** para reutilização
- ✅ **Estrutura de pastas organizada** por tipo de arquivo
- ✅ **Testes automatizados** estruturados
- ✅ **Documentação completa** e atualizada
- ✅ **Setup.py** para instalação como pacote

## 🏗️ Arquitetura

### Módulos Principais

1. **pje_client.py** - Cliente principal
   - Classe `PJeClient` com métodos organizados
   - Context manager para cleanup automático
   - Logging estruturado
   - Screenshots automáticos

2. **config.py** - Configurações
   - URLs e endpoints
   - Timeouts e limites
   - Seletores CSS/XPath
   - Opções do browser

3. **exceptions.py** - Exceções
   - `PJeAutomationError` (base)
   - `LoginError`
   - `ProcessNotFoundError`
   - `DownloadError`
   - `NavigationError`
   - `ElementNotFoundError`

4. **utils.py** - Utilitários
   - Setup de logging
   - Manipulação de arquivos
   - Parsing de números de processo
   - Formatação de dados

### Melhorias Implementadas

#### ✅ Separação de Responsabilidades
- Cada módulo tem uma responsabilidade específica
- Código mais limpo e legível
- Facilita manutenção e debugging

#### ✅ Configuração Centralizada
- Todas as configurações em um local
- Fácil modificação sem alterar código
- Suporte a diferentes ambientes

#### ✅ Tratamento de Erros Robusto
- Exceções específicas para cada tipo de erro
- Messages de erro mais informativos
- Melhor debugging

#### ✅ Logging Profissional
- Diferentes níveis de log
- Arquivos de log organizados
- Formatação padronizada

#### ✅ Estrutura de Pastas
- Arquivos organizados por tipo
- Fácil navegação
- Separação entre código e dados

#### ✅ Testabilidade
- Módulos pequenos e testáveis
- Estrutura de testes organizada
- Mocking facilitado

#### ✅ Documentação
- README completo e atualizado
- Docstrings em todas as funções
- Exemplos de uso

#### ✅ Instalabilidade
- Setup.py configurado
- Installação como pacote Python
- Entry points definidos

## 🚀 Como Usar a Nova Estrutura

### Execução Direta
```bash
python main.py
```

### Uso Programático
```python
from src.pje_automation import PJeClient

with PJeClient() as client:
    client.login()
    client.search_process("5100342-29.2017.8.13.0024")
    file_path = client.download_process_document("5100342-29.2017.8.13.0024")
```

### Configuração Personalizada
```python
from src.pje_automation.config import PJeConfig

PJeConfig.DEFAULT_TIMEOUT = 60
PJeConfig.DATA_DIR = "meus_downloads"
```

### Executar Testes
```bash
python -m pytest tests/ -v
```

## 📈 Benefícios da Reorganização

1. **Manutenibilidade** ⬆️
   - Código mais fácil de entender e modificar
   - Separação clara de responsabilidades

2. **Escalabilidade** ⬆️
   - Fácil adição de novas funcionalidades
   - Estrutura que suporta crescimento

3. **Testabilidade** ⬆️
   - Módulos pequenos e focados
   - Testes mais simples de escrever

4. **Reutilização** ⬆️
   - Utilitários podem ser usados em outros projetos
   - Configurações padronizadas

5. **Colaboração** ⬆️
   - Estrutura familiar para desenvolvedores Python
   - Documentação clara

6. **Profissionalismo** ⬆️
   - Estrutura de projeto padrão da indústria
   - Boas práticas implementadas

---

**🎉 Projeto reorganizado com sucesso seguindo as melhores práticas de desenvolvimento Python!**
