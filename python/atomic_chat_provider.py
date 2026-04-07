"""
atomic_chat_provider.py
-----------------------
Adiciona suporte nativo ao Atomic Chat no openclaude.
Permite que o Claude Code roteie requisições para qualquer modelo local rodando via
Atomic Chat (apenas Apple Silicon) em 127.0.0.1:1337.

O Atomic Chat expõe uma API compatível com OpenAI, então as mensagens são encaminhadas
diretamente sem tradução.

Uso (.env):
    PREFERRED_PROVIDER=atomic-chat
    ATOMIC_CHAT_BASE_URL=http://127.0.0.1:1337
"""

# Importa httpx para fazer requisições HTTP assíncronas
import httpx
# Importa json para serialização/deserialização de dados JSON
import json
# Importa logging para registro de logs
import logging
# Importa os para acessar variáveis de ambiente
import os
# Importa AsyncIterator para tipar geradores assíncronos
from typing import AsyncIterator

# Cria um logger com o nome do módulo atual para registro de logs
logger = logging.getLogger(__name__)
# Obtém a URL base do Atomic Chat da variável de ambiente, ou usa o padrão localhost:1337
ATOMIC_CHAT_BASE_URL = os.getenv("ATOMIC_CHAT_BASE_URL", "http://127.0.0.1:1337")


def _api_url(path: str) -> str:
    """Constrói a URL completa da API concatenando a URL base com o caminho /v1 e o endpoint."""
    return f"{ATOMIC_CHAT_BASE_URL}/v1{path}"


async def check_atomic_chat_running() -> bool:
    """Verifica se o serviço Atomic Chat está rodando tentando acessar o endpoint /models."""
    try:
        # Cria um cliente HTTP assíncrono com timeout de 3 segundos
        async with httpx.AsyncClient(timeout=3.0) as client:
            # Faz uma requisição GET para o endpoint de modelos
            resp = await client.get(_api_url("/models"))
            # Retorna True se o status for 200 (OK)
            return resp.status_code == 200
    except Exception:
        # Em caso de qualquer erro (conexão recusada, timeout, etc.), retorna False
        return False


async def list_atomic_chat_models() -> list[str]:
    """Lista todos os modelos disponíveis no Atomic Chat."""
    try:
        # Cria um cliente HTTP assíncrono com timeout de 5 segundos
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Faz uma requisição GET para o endpoint de modelos
            resp = await client.get(_api_url("/models"))
            # Lança exceção se o status não for 2xx
            resp.raise_for_status()
            # Decodifica a resposta JSON
            data = resp.json()
            # Extrai e retorna uma lista com os IDs dos modelos
            return [m["id"] for m in data.get("data", [])]
    except Exception as e:
        # Em caso de erro, registra um aviso e retorna lista vazia
        logger.warning(f"Não foi possível listar modelos do Atomic Chat: {e}")
        return []


async def atomic_chat(
    model: str,                      # Nome/ID do modelo a ser usado
    messages: list[dict],            # Lista de mensagens da conversa
    system: str | None = None,       # Prompt de sistema opcional
    max_tokens: int = 4096,          # Número máximo de tokens na resposta
    temperature: float = 1.0,        # Temperatura para controle de aleatoriedade
) -> dict:
    """Envia uma requisição de chat para o Atomic Chat (sem streaming) e retorna a resposta formatada."""
    # Cria uma cópia da lista de mensagens para não modificar o original
    chat_messages = list(messages)
    # Se houver prompt de sistema, insere como primeira mensagem com role "system"
    if system:
        chat_messages.insert(0, {"role": "system", "content": system})

    # Monta o payload da requisição no formato OpenAI
    payload = {
        "model": model,              # Modelo a ser usado
        "messages": chat_messages,   # Mensagens da conversa
        "max_tokens": max_tokens,    # Limite de tokens da resposta
        "temperature": temperature,  # Temperatura de geração
        "stream": False,             # Não usa streaming
    }

    # Faz a requisição POST para o endpoint de chat completions
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(_api_url("/chat/completions"), json=payload)
        resp.raise_for_status()  # Lança exceção se status não for 2xx
        data = resp.json()       # Decodifica a resposta JSON

    # Extrai o texto da resposta do assistente
    choice = data.get("choices", [{}])[0]
    assistant_text = choice.get("message", {}).get("content", "")
    # Extrai informações de uso de tokens
    usage = data.get("usage", {})

    # Retorna a resposta no formato compatível com a API da Anthropic
    return {
        "id": data.get("id", "msg_atomic_chat"),       # ID da mensagem
        "type": "message",                               # Tipo do objeto
        "role": "assistant",                             # Papel (assistente)
        "content": [{"type": "text", "text": assistant_text}],  # Conteúdo da resposta
        "model": model,                                  # Modelo utilizado
        "stop_reason": "end_turn",                       # Razão de parada
        "stop_sequence": None,                           # Sequência de parada (nenhuma)
        "usage": {
            "input_tokens": usage.get("prompt_tokens", 0),      # Tokens de entrada
            "output_tokens": usage.get("completion_tokens", 0),  # Tokens de saída
        },
    }


async def atomic_chat_stream(
    model: str,                      # Nome/ID do modelo a ser usado
    messages: list[dict],            # Lista de mensagens da conversa
    system: str | None = None,       # Prompt de sistema opcional
    max_tokens: int = 4096,          # Número máximo de tokens na resposta
    temperature: float = 1.0,        # Temperatura para controle de aleatoriedade
) -> AsyncIterator[str]:
    """Envia uma requisição de chat com streaming e retorna eventos SSE no formato Anthropic."""
    # Cria uma cópia da lista de mensagens
    chat_messages = list(messages)
    # Insere o prompt de sistema se fornecido
    if system:
        chat_messages.insert(0, {"role": "system", "content": system})

    # Monta o payload da requisição com streaming habilitado
    payload = {
        "model": model,
        "messages": chat_messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": True,              # Habilita streaming
    }

    # Emite o evento de início da mensagem no formato SSE (Server-Sent Events)
    yield "event: message_start\n"
    yield f'data: {json.dumps({"type": "message_start", "message": {"id": "msg_atomic_chat_stream", "type": "message", "role": "assistant", "content": [], "model": model, "stop_reason": None, "usage": {"input_tokens": 0, "output_tokens": 0}}})}\n\n'
    # Emite o evento de início do bloco de conteúdo
    yield "event: content_block_start\n"
    yield f'data: {json.dumps({"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}})}\n\n'

    # Faz a requisição POST com streaming
    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream("POST", _api_url("/chat/completions"), json=payload) as resp:
            resp.raise_for_status()  # Verifica se o status é OK
            # Itera sobre cada linha da resposta stream
            async for line in resp.aiter_lines():
                # Ignora linhas vazias ou que não começam com "data: "
                if not line or not line.startswith("data: "):
                    continue
                # Remove o prefixo "data: " da linha
                raw = line[len("data: "):]
                # Se a linha é [DONE], o stream terminou
                if raw.strip() == "[DONE]":
                    break
                try:
                    # Decodifica o chunk JSON
                    chunk = json.loads(raw)
                    # Extrai o delta (texto incremental) da resposta
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    delta_text = delta.get("content", "")
                    # Se há texto novo, emite um evento de delta de conteúdo
                    if delta_text:
                        yield "event: content_block_delta\n"
                        yield f'data: {json.dumps({"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": delta_text}})}\n\n'

                    # Verifica se há uma razão de término (modelo terminou de gerar)
                    finish_reason = chunk.get("choices", [{}])[0].get("finish_reason")
                    if finish_reason:
                        # Obtém estatísticas de uso de tokens
                        usage = chunk.get("usage", {})
                        # Emite eventos de finalização do bloco de conteúdo
                        yield "event: content_block_stop\n"
                        yield f'data: {json.dumps({"type": "content_block_stop", "index": 0})}\n\n'
                        # Emite o delta final da mensagem com razão de parada e uso
                        yield "event: message_delta\n"
                        yield f'data: {json.dumps({"type": "message_delta", "delta": {"stop_reason": "end_turn", "stop_sequence": None}, "usage": {"output_tokens": usage.get("completion_tokens", 0)}})}\n\n'
                        # Emite o evento de parada da mensagem
                        yield "event: message_stop\n"
                        yield f'data: {json.dumps({"type": "message_stop"})}\n\n'
                        break  # Sai do loop de streaming
                except json.JSONDecodeError:
                    # Ignora linhas com JSON malformado
                    continue
