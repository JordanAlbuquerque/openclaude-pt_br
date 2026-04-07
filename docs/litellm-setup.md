# Configuração do LiteLLM

O OpenClaude pode se conectar ao LiteLLM através do proxy compatível com OpenAI do LiteLLM.

## Visão Geral

O LiteLLM é um gateway LLM open-source que fornece uma API unificada para mais de 100 provedores de modelos. Ao executar o Proxy LiteLLM, você pode rotear as requisições do OpenClaude pelo LiteLLM para acessar qualquer um de seus provedores suportados — tudo usando o caminho de provedor compatível com OpenAI já existente no OpenClaude.

## Pré-requisitos

- LiteLLM instalado (`pip install litellm[proxy]`)
- Um `litellm_config.yaml` ou configuração equivalente do LiteLLM
- Proxy LiteLLM rodando em uma porta local ou remota

## 1. Iniciar o Proxy LiteLLM

### Instalação básica

```bash
pip install litellm[proxy]
```

### Configurar o LiteLLM

Crie um `litellm_config.yaml` com os aliases de modelo desejados:

```yaml
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_API_KEY

  - model_name: claude-sonnet-4
    litellm_params:
      model: anthropic/claude-sonnet-4-5-20250929
      api_key: os.environ/ANTHROPIC_API_KEY

  - model_name: gemini-2.5-flash
    litellm_params:
      model: gemini/gemini-2.5-flash
      api_key: os.environ/GEMINI_API_KEY

  - model_name: llama-3.3-70b
    litellm_params:
      model: together_ai/meta-llama/Llama-3.3-70B-Instruct-Turbo
      api_key: os.environ/TOGETHER_API_KEY
```

### Executar o proxy

```bash
litellm --config litellm_config.yaml --port 4000
```

O proxy iniciará em `http://localhost:4000` por padrão.

## 2. Apontar o OpenClaude para o LiteLLM

### Opção A: Variáveis de Ambiente

```bash
export CLAUDE_CODE_USE_OPENAI=1
export OPENAI_BASE_URL=http://localhost:4000
export OPENAI_API_KEY=<sua-master-key-ou-placeholder>
export OPENAI_MODEL=<seu-alias-de-modelo-litellm>
openclaude
```

Substitua `<seu-alias-de-modelo-litellm>` por um nome de modelo do seu `litellm_config.yaml` (ex: `gpt-4o`, `claude-sonnet-4`, `gemini-2.5-flash`).

### Opção B: Usando /provider

1. Execute `openclaude`
2. Digite `/provider` para abrir o fluxo de configuração de provedor
3. Escolha a opção **OpenAI-compatible**
4. Quando solicitado a API key, insira a chave exigida pelo seu proxy LiteLLM
   Se sua configuração local do LiteLLM não exige autenticação, pode ser necessário inserir um valor placeholder
5. Quando solicitado a URL base, insira `http://localhost:4000`
6. Quando solicitado o modelo, insira o nome ou alias do modelo LiteLLM que você configurou
7. Salve a configuração do provedor

## 3. Exemplos de Configurações do LiteLLM

### Roteamento multi-provedor com rastreamento de gastos

```yaml
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_API_KEY

  - model_name: claude-sonnet-4
    litellm_params:
      model: anthropic/claude-sonnet-4-5-20250929
      api_key: os.environ/ANTHROPIC_API_KEY

  - model_name: deepseek-chat
    litellm_params:
      model: deepseek/deepseek-chat
      api_key: os.environ/DEEPSEEK_API_KEY

litellm_settings:
  set_verbose: false
  num_retries: 3
```

### Com uma master key para autenticação

```bash
# Iniciar proxy com master key
litellm --config litellm_config.yaml --port 4000 --master_key sk-my-master-key

# Conectar o OpenClaude
export CLAUDE_CODE_USE_OPENAI=1
export OPENAI_BASE_URL=http://localhost:4000
export OPENAI_API_KEY=sk-my-master-key
export OPENAI_MODEL=gpt-4o
openclaude
```

## 4. Observações

- `OPENAI_MODEL` deve corresponder ao **alias de modelo do LiteLLM** definido na sua configuração, não ao nome bruto do modelo do provedor upstream.
- Se seu proxy requer autenticação, use a chave do proxy (ou `master_key`) em `OPENAI_API_KEY`.
- O endpoint compatível com OpenAI do LiteLLM aceita o mesmo formato de requisição que a OpenAI, então o OpenClaude funciona sem nenhuma alteração de código.
- Você pode alternar entre qualquer provedor configurado no LiteLLM simplesmente mudando o valor de `OPENAI_MODEL` — sem necessidade de reconfigurar o OpenClaude.

## 5. Solução de Problemas

| Problema | Causa Provável | Correção |
|-------|--------------|--------|
| 404 ou Modelo Não Encontrado | Alias do modelo não existe na configuração do LiteLLM | Verifique se o `model_name` no `litellm_config.yaml` corresponde ao `OPENAI_MODEL` |
| Conexão Recusada | Proxy do LiteLLM não está rodando | Inicie o proxy com `litellm --config litellm_config.yaml --port 4000` |
| Falha na Autenticação | `master_key` ausente ou incorreta | Defina a chave correta em `OPENAI_API_KEY` |
| Erro no provedor upstream | A chave da API do provedor backend está ausente ou inválida | Certifique-se de que a API key upstream (ex: `OPENAI_API_KEY`) está definida no ambiente do processo do proxy LiteLLM |
| Ferramentas falham mas chat funciona | O modelo selecionado tem suporte fraco a chamada de funções/ferramentas | Mude para um modelo com bom suporte a ferramentas (ex: GPT-4o, Claude Sonnet) |

## 6. Recursos

- [Documentação do Proxy LiteLLM](https://docs.litellm.ai/docs/proxy/quick_start)
- [Lista de Provedores do LiteLLM](https://docs.litellm.ai/docs/providers)
- [Endpoints Compatíveis com OpenAI do LiteLLM](https://docs.litellm.ai/docs/proxy/openai_compatible_proxy)
