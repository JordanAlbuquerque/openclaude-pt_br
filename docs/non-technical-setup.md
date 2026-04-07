# OpenClaude para Usuários Não Técnicos

Este guia é para pessoas que querem o caminho de configuração mais fácil.

Você não precisa compilar a partir do código-fonte. Você não precisa do Bun. Você não precisa entender toda a base de código.

Se você consegue copiar e colar comandos em um terminal, você consegue configurar isso.

## O Que o OpenClaude Faz

O OpenClaude permite que você use um assistente de programação com IA com diferentes provedores de modelos, como:

- OpenAI
- DeepSeek
- Gemini
- Ollama
- Codex

Para a maioria dos usuários iniciantes, a OpenAI é a opção mais fácil.

## Antes de Começar

Você precisa de:

1. Node.js 20 ou mais recente instalado
2. Uma janela de terminal
3. Uma API key do seu provedor, a menos que você esteja usando um modelo local como o Ollama

## Caminho Mais Rápido

1. Instale o OpenClaude com npm
2. Defina 3 variáveis de ambiente
3. Execute `openclaude`

## Escolha Seu Sistema Operacional

- Windows: [Início Rápido no Windows](quick-start-windows.md)
- macOS / Linux: [Início Rápido no macOS / Linux](quick-start-mac-linux.md)

## Qual Provedor Você Deve Escolher?

### OpenAI

Escolha este se:

- você quer a configuração mais fácil
- você já tem uma API key da OpenAI

### Ollama

Escolha este se:

- você quer executar modelos localmente
- você não quer depender de uma API na nuvem para testes

### Codex

Escolha este se:

- você já usa o CLI do Codex
- você já tem autenticação do Codex ou ChatGPT configurada

## Como É o Sucesso

Após executar `openclaude`, o CLI deve iniciar e aguardar seu prompt.

Nesse ponto, você pode pedir para ele:

- explicar código
- editar arquivos
- executar comandos
- revisar alterações

## Problemas Comuns

### Comando `openclaude` não encontrado

Causa:

- O npm instalou o pacote, mas seu terminal ainda não atualizou

Correção:

1. Feche o terminal
2. Abra um novo terminal
3. Execute `openclaude` novamente

### API key inválida

Causa:

- A chave está errada, expirada ou copiada incorretamente

Correção:

1. Obtenha uma chave nova do seu provedor
2. Cole novamente com cuidado
3. Execute `openclaude` novamente

### Ollama não funciona

Causa:

- O Ollama não está instalado ou não está rodando

Correção:

1. Instale o Ollama de `https://ollama.com/download`
2. Inicie o Ollama
3. Tente novamente

## Quer Mais Controle?

Se você quer builds a partir do código-fonte, perfis avançados de provedores, diagnósticos ou fluxos de trabalho baseados em Bun, use:

- [Configuração Avançada](advanced-setup.md)
