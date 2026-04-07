# Início Rápido do OpenClaude para Windows

Este guia usa o Windows PowerShell.

## 1. Instalar o Node.js

Instale o Node.js 20 ou mais recente de:

- `https://nodejs.org/`

Depois abra o PowerShell e verifique:

```powershell
node --version
npm --version
```

## 2. Instalar o OpenClaude

```powershell
npm install -g @gitlawb/openclaude
```

## 3. Escolha Um Provedor

### Opção A: OpenAI

Substitua `sk-your-key-here` pela sua chave real.

```powershell
$env:CLAUDE_CODE_USE_OPENAI="1"
$env:OPENAI_API_KEY="sk-your-key-here"
$env:OPENAI_MODEL="gpt-4o"

openclaude
```

### Opção B: DeepSeek

```powershell
$env:CLAUDE_CODE_USE_OPENAI="1"
$env:OPENAI_API_KEY="sk-your-key-here"
$env:OPENAI_BASE_URL="https://api.deepseek.com/v1"
$env:OPENAI_MODEL="deepseek-chat"

openclaude
```

### Opção C: Ollama

Instale o Ollama primeiro de:

- `https://ollama.com/download/windows`

Depois execute:

```powershell
ollama pull llama3.1:8b

$env:CLAUDE_CODE_USE_OPENAI="1"
$env:OPENAI_BASE_URL="http://localhost:11434/v1"
$env:OPENAI_MODEL="llama3.1:8b"

openclaude
```

Nenhuma API key é necessária para modelos locais do Ollama.

### Opção D: LM Studio

Instale o LM Studio primeiro de:

- `https://lmstudio.ai/`

Depois no LM Studio:

1. Baixe um modelo (ex: Llama 3.1 8B, Mistral 7B)
2. Vá para a aba "Developer"
3. Selecione seu modelo e habilite o servidor pelo toggle

Depois execute:

```powershell
$env:CLAUDE_CODE_USE_OPENAI="1"
$env:OPENAI_BASE_URL="http://localhost:1234/v1"
$env:OPENAI_MODEL="seu-nome-de-modelo"
# $env:OPENAI_API_KEY="lmstudio"  # opcional: alguns usuários precisam de uma chave dummy

openclaude
```

Substitua `seu-nome-de-modelo` pelo nome do modelo mostrado no LM Studio.

Nenhuma API key é necessária para modelos locais do LM Studio (mas descomente a linha `OPENAI_API_KEY` se você receber erros de autenticação).

## 4. Se o `openclaude` Não For Encontrado

Feche o PowerShell, abra um novo e tente novamente:

```powershell
openclaude
```

## 5. Se Seu Provedor Falhar

Verifique o básico:

### Para OpenAI ou DeepSeek

- certifique-se de que a chave é real
- certifique-se de que você copiou completamente

### Para Ollama

- certifique-se de que o Ollama está instalado
- certifique-se de que o Ollama está rodando
- certifique-se de que o modelo foi baixado com sucesso

### Para LM Studio

- certifique-se de que o LM Studio está instalado
- certifique-se de que o LM Studio está rodando
- certifique-se de que o servidor está habilitado (toggle ligado na aba "Developer")
- certifique-se de que um modelo está carregado no LM Studio
- certifique-se de que o nome do modelo corresponde ao que você definiu em `OPENAI_MODEL`

## 6. Atualizando o OpenClaude

```powershell
npm install -g @gitlawb/openclaude@latest
```

## 7. Desinstalando o OpenClaude

```powershell
npm uninstall -g @gitlawb/openclaude
```

## Precisa de Configuração Avançada?

Use:

- [Configuração Avançada](advanced-setup.md)
