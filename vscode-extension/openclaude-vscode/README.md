# Extensão OpenClaude para VS Code

Uma extensão prática para o VS Code como companheiro do OpenClaude, com um **Centro de Controle** ciente do projeto, comportamento previsível de inicialização no terminal e acesso rápido a fluxos de trabalho úteis do OpenClaude.

## Funcionalidades

- **Status real do Centro de Controle** na Barra de Atividades:
  - se o comando `openclaude` configurado está instalado
  - o comando de inicialização sendo usado
  - se o shim de inicialização injeta `CLAUDE_CODE_USE_OPENAI=1`
  - a pasta do workspace atual
  - o cwd de inicialização que será usado para sessões de terminal
  - se o `.openclaude-profile.json` existe na raiz do workspace atual
  - um resumo conservador do provedor derivado do perfil do workspace ou flags de ambiente conhecidas
- **Comportamento de inicialização ciente do projeto**:
  - `Launch OpenClaude` inicia a partir do workspace do editor ativo quando possível
  - faz fallback para a primeira pasta do workspace quando necessário
  - evita iniciar a partir de um cwd padrão arbitrário quando um projeto está aberto
- **Ações práticas na barra lateral**:
  - Iniciar OpenClaude
  - Iniciar na Raiz do Workspace
  - Abrir Perfil do Workspace
  - Abrir Repositório
  - Abrir Guia de Configuração
  - Abrir Paleta de Comandos
- **Tema escuro integrado**: `OpenClaude Terminal Black`

## Requisitos

- VS Code `1.95+`
- `openclaude` disponível no PATH do seu terminal (`npm install -g @gitlawb/openclaude`)

## Comandos

- `OpenClaude: Open Control Center`
- `OpenClaude: Launch in Terminal`
- `OpenClaude: Launch in Workspace Root`
- `OpenClaude: Open Repository`
- `OpenClaude: Open Setup Guide`
- `OpenClaude: Open Workspace Profile`

## Configurações

- `openclaude.launchCommand` (padrão: `openclaude`)
- `openclaude.terminalName` (padrão: `OpenClaude`)
- `openclaude.useOpenAIShim` (padrão: `false`)

`openclaude.useOpenAIShim` apenas injeta `CLAUDE_CODE_USE_OPENAI=1` nos terminais iniciados pela extensão. Ele não adivinha nem configura um provedor por conta própria.

## Observações sobre Detecção de Status

- O status do provedor prefere o arquivo real `.openclaude-profile.json` do workspace quando presente.
- Se nenhum perfil salvo existir, a extensão faz fallback para flags de ambiente conhecidas disponíveis para o host da extensão do VS Code.
- Se a fonte da verdade não estiver clara, a extensão mostra `unknown` em vez de adivinhar.

## Desenvolvimento

A partir desta pasta:

```bash
npm run test
npm run lint
```

Para empacotar (opcional):

```bash
npm run package
```
