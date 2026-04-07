# Política de Segurança

## Versões Suportadas

O Open Claude é mantido atualmente apenas na branch `main` mais recente e na
última versão publicada no npm.

| Versão | Suportada |
| ------- | --------- |
| Última versão publicada | :white_check_mark: |
| Versões anteriores | :x: |
| Forks não lançados / builds modificados | :x: |

Correções de segurança geralmente são lançadas na próxima versão de patch e também podem ser
aplicadas diretamente na `main` antes de uma publicação do pacote.

## Reportando uma Vulnerabilidade

Se você acredita ter encontrado uma vulnerabilidade de segurança no Open Claude,
por favor reporte de forma privada.

Canal de reporte preferido:

- GitHub Security Advisories / reporte privado de vulnerabilidades para este
  repositório

Por favor inclua:

- uma descrição clara do problema
- versão afetada, commit ou ambiente
- passos para reprodução ou prova de conceito
- avaliação do impacto
- qualquer sugestão de correção, se disponível

Por favor, **não** abra uma issue pública para uma vulnerabilidade sem correção.

## Processo de Resposta

Nossos objetivos gerais são:

- confirmação inicial de triagem em até 7 dias
- acompanhamento após validação quando conseguirmos reproduzir o problema
- divulgação coordenada após uma correção estar disponível

Severidade, explorabilidade e disponibilidade da equipe de manutenção podem afetar os prazos.

## Divulgação e CVEs

Relatórios válidos podem ser corrigidos de forma privada primeiro e divulgados após um patch
estar disponível.

Se um relatório for aceito e o problema for significativo o suficiente para justificar
rastreamento formal, podemos publicar um GitHub Security Advisory e solicitar ou atribuir um CVE
pelo canal apropriado. A emissão de CVE não é garantida para todos os
relatórios.

## Escopo

Esta política se aplica a:

- o código-fonte do Open Claude neste repositório
- artefatos oficiais de release publicados a partir deste repositório
- o pacote npm `@gitlawb/openclaude`

Esta política não cobre:

- provedores de modelos, endpoints ou serviços hospedados de terceiros
- configuração incorreta local na máquina do relator
- vulnerabilidades em forks não oficiais, mirrors ou redistribuições downstream
