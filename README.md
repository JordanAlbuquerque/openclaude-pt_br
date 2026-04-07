# OpenClaude

OpenClaude é um CLI de agente de programação open-source para provedores de modelos na nuvem e locais.

Use APIs compatíveis com OpenAI, Gemini, GitHub Models, Codex, Ollama, Atomic Chat e outros backends suportados, mantendo um único fluxo de trabalho centrado no terminal: prompts, ferramentas, agentes, MCP, comandos slash e saída em streaming.

[Quick Start](#quick-start) | [Guias de Configuração](#setup-guides) | [Provedores](#supported-providers) | [Build do Código](#source-build-and-local-development) | [Extensão VS Code](#vs-code-extension) | [Comunidade](#community)

## Por que OpenClaude

- Use um único CLI para APIs na nuvem e backends locais
- Salve perfis de provedores dentro do app com `/provider`
- Execute com serviços compatíveis com OpenAI, Gemini, GitHub Models, Codex, Ollama, Atomic Chat e outros provedores suportados
- Mantenha fluxos de trabalho de coding-agent em um só lugar: bash, ferramentas de arquivo, grep, glob, agentes, tarefas, MCP e ferramentas web
- Use a extensão integrada do VS Code para integração de execução e suporte a temas

## Início Rápido
### Verifiquem se o Node está instalado caso não instalem..
```
node --version
npm --version
```
Depois 
### Instalar OpenClaude

```bash
npm install -g @gitlawb/openclaude
```

Se a instalação depois mostrar `ripgrep not found`, instale o ripgrep no sistema e confirme que `rg --version` funciona no mesmo terminal antes de iniciar o OpenClaude.

### Iniciar

```bash
openclaude
```

Dentro do OpenClaude:

- execute `/provider` para configuração guiada de provedores e perfis salvos  
- execute `/onboard-github` para onboarding do GitHub Models  

### Configuração mais rápida com OpenAI

macOS / Linux:

```bash
export CLAUDE_CODE_USE_OPENAI=1
export OPENAI_API_KEY=sk-your-key-here
export OPENAI_MODEL=gpt-4o

openclaude
```

Windows PowerShell:

```powershell
$env:CLAUDE_CODE_USE_OPENAI="1"
$env:OPENAI_API_KEY="sk-your-key-here"
$env:OPENAI_MODEL="gpt-4o"

openclaude
```

### Configuração local mais rápida com Ollama

macOS / Linux:

```bash
export CLAUDE_CODE_USE_OPENAI=1
export OPENAI_BASE_URL=http://localhost:11434/v1
export OPENAI_MODEL=qwen2.5-coder:7b

openclaude
```

Windows PowerShell:

```powershell
$env:CLAUDE_CODE_USE_OPENAI="1"
$env:OPENAI_BASE_URL="http://localhost:11434/v1"
$env:OPENAI_MODEL="qwen2.5-coder:7b"

openclaude
```
### Configuração com OPENROUTER+VSCODE
```
$env:CLAUDE_CODE_USE_OPENAI="1"
$env:OPENAI_BASE_URL="https://openrouter.ai/api/v1"
$env:OPENAI_API_KEY="API OPEN ROUTER"
$env:OPENAI_MODEL="qwen/qwen3.6-plus:free"
```

## Guias de Configuração

Guias para iniciantes:

- Non-Technical Setup → Configuração não técnica  
- Windows Quick Start → Início rápido no Windows  
- macOS / Linux Quick Start → Início rápido no macOS/Linux  

Guias avançados:

- Advanced Setup → Configuração avançada  
- Android Install → Instalação no Android  

## Provedores Suportados

| Provedor | Caminho de configuração | Observações |
| --- | --- | --- |
| OpenAI-compatible | `/provider` ou variáveis de ambiente | Funciona com OpenAI, OpenRouter, DeepSeek, Groq, Mistral, LM Studio e outros servidores `/v1` |
| Gemini | `/provider` ou variáveis de ambiente | Suporta API key, token ou fluxo ADC local |
| GitHub Models | `/onboard-github` | Onboarding interativo com credenciais salvas |
| Codex | `/provider` | Usa credenciais existentes do Codex |
| Ollama | `/provider` ou variáveis de ambiente | Execução local sem API key |
| Atomic Chat | configuração avançada | Backend local Apple Silicon |
| Bedrock / Vertex / Foundry | variáveis de ambiente | Integrações adicionais |

## O que funciona

- **Workflows de programação com ferramentas**  
- **Respostas em streaming**  
- **Chamadas de ferramentas**  
- **Imagens (URL e base64)**  
- **Perfis de provedores**  
- **Modelos locais e remotos**  

## Observações sobre provedores

- Funcionalidades específicas da Anthropic podem não existir em outros provedores  
- A qualidade depende do modelo escolhido  
- Modelos locais pequenos podem ter dificuldade com fluxos complexos  
- Alguns provedores têm limites menores de saída  

## Roteamento de Agentes

```json
{
  "agentModels": {
    "deepseek-chat": {
      "base_url": "https://api.deepseek.com/v1",
      "api_key": "sk-your-key"
    },
    "gpt-4o": {
      "base_url": "https://api.openai.com/v1",
      "api_key": "sk-your-key"
    }
  },
  "agentRouting": {
    "Explore": "deepseek-chat",
    "Plan": "gpt-4o",
    "general-purpose": "gpt-4o",
    "frontend-dev": "deepseek-chat",
    "default": "gpt-4o"
  }
}
```

> **Nota:** `api_key` é armazenado em texto plano.

## Web Search e Fetch

Por padrão, `WebSearch` usa DuckDuckGo em modelos não-Anthropic.

Para melhor confiabilidade, use Firecrawl:

```bash
export FIRECRAWL_API_KEY=your-key-here
```

## Servidor gRPC Headless

```bash
npm run dev:grpc
```

Cliente CLI:

```bash
npm run dev:grpc:cli
```
## Construção do código-fonte e desenvolvimento local
  
Build do Código

```bash
bun install
bun run build
node dist/cli.mjs
```

## Testes

```bash
bun test
bun run test:coverage
```

## Estrutura do Repositório

- `src/` - núcleo  
- `scripts/` - scripts  
- `docs/` - documentação  
- `python/` - helpers Python  
- `vscode-extension/` - extensão VS Code  
- `.github/` - automações  
- `bin/` - entrada CLI  

## Extensão VS Code

Inclui integração de execução e UI de controle de provedores.

## Segurança

Veja `SECURITY.md`.
