# Contribuindo com o OpenClaude

Obrigado por contribuir.

O OpenClaude é um CLI de agente de programação open-source em rápida evolução, com suporte a múltiplos provedores, backends locais, MCP e fluxo de trabalho centrado no terminal. As melhores contribuições são focadas, bem testadas e fáceis de revisar.

## Antes de Começar

- Pesquise nas [issues](https://github.com/Gitlawb/openclaude/issues) e [discussions](https://github.com/Gitlawb/openclaude/discussions) existentes antes de abrir uma nova thread.
- Use issues para bugs confirmados e trabalho de funcionalidades acionáveis.
- Use discussions para ajuda com configuração, ideias e conversas gerais da comunidade.
- Para mudanças maiores, abra uma issue primeiro para que o escopo fique claro antes da implementação.
- Para relatórios de segurança, siga o [SECURITY.md](SECURITY.md).

## Configuração Local

Instalar dependências:

```bash
bun install
```

Compilar o CLI:

```bash
bun run build
```

Teste de fumaça:

```bash
bun run smoke
```

Executar o app localmente:

```bash
bun run dev
```

Se você estiver trabalhando com configuração de provedores ou perfis salvos, comandos úteis incluem:

```bash
bun run profile:init
bun run dev:profile
```

## Fluxo de Trabalho de Desenvolvimento

- Mantenha os PRs focados em um problema ou funcionalidade.
- Evite misturar limpeza não relacionada na mesma mudança.
- Preserve os padrões existentes do repositório a menos que a mudança seja intencionalmente uma refatoração.
- Adicione ou atualize testes quando a mudança afetar o comportamento.
- Atualize a documentação quando a configuração, comandos ou comportamento visível ao usuário mudar.

## Validação

No mínimo, execute as verificações mais relevantes para sua mudança.

Verificações comuns:

```bash
bun run build
bun run smoke
```

Testes focados:

```bash
bun test ./caminho/para/arquivo-de-teste.test.ts
```

Quando estiver trabalhando com configuração de provedores/runtime, isso também pode ajudar:

```bash
bun run doctor:runtime
```

## Pull Requests

Bons PRs geralmente incluem:

- uma breve explicação do que mudou
- por que mudou
- o impacto no usuário ou desenvolvedor
- as verificações exatas que você executou

Se o PR alterar UI, apresentação no terminal ou a extensão do VS Code, inclua capturas de tela quando útil.

Se o PR alterar o comportamento do provedor, mencione qual caminho de provedor foi testado.

## Estilo de Código

- Siga o estilo de código existente nos arquivos modificados.
- Prefira mudanças pequenas e legíveis em vez de reescritas amplas.
- Não reformate arquivos não relacionados só porque estão próximos.
- Mantenha comentários úteis e concisos.

## Mudanças em Provedores

O OpenClaude suporta múltiplos caminhos de provedores. Se você alterar a lógica de provedores:

- seja explícito sobre quais provedores são afetados
- evite quebrar provedores de terceiros ao corrigir comportamento de primeira parte
- teste o caminho exato do provedor/modelo que você alterou quando possível
- destaque quaisquer limitações ou trabalho de acompanhamento na descrição do PR

## Comunidade

Por favor, seja respeitoso e construtivo com outros contribuidores.

Os mantenedores podem solicitar:

- escopo mais restrito
- PRs de acompanhamento focados
- validação mais robusta
- atualizações de documentação para mudanças de comportamento

Isso é normal e ajuda a manter o projeto revisável conforme ele cresce.
