"""
ollama_provider.py
------------------
Adiciona suporte nativo ao Ollama no openclaude.
Permite que o Claude Code roteie requisições para qualquer modelo Ollama local
(llama3, mistral, codellama, phi3, qwen2, deepseek-coder, etc.)
sem precisar de uma API key.

Uso (.env):
    PREFERRED_PROVIDER=ollama
    OLLAMA_BASE_URL=http://localhost:11434
    BIG_MODEL=codellama:34b
    SMALL_MODEL=llama3:8b
"""

# Importa httpx para fazer requisições HTTP assíncronas
import httpx
# Importa logging para registro de logs
import logging
# Importa os para acessar variáveis de ambiente
import os
# Importa AsyncIterator para tipar geradores assíncronos
from typing import AsyncIterator

# Cria um logger com o nome do módulo atual
logger = logging.getLogger(__name__)
# Obtém a URL base do Ollama da variável de ambiente, ou usa o padrão localhost:11434
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


async def check_ollama_running() -> bool:
    """Verifica se o serviço Ollama está rodando tentando acessar o endpoint /api/tags."""
    try:
        # Cria um cliente HTTP assíncrono com timeout de 3 segundos
        async with httpx.AsyncClient(timeout=3.0) as client:
            # Faz uma requisição GET para o endpoint de tags (lista de modelos)
            resp = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            # Retorna True se o status for 200 (OK)
            return resp.status_code == 200
    except Exception:
        # Em caso de erro (conexão recusada, timeout, etc.), retorna False
        return False


async def list_ollama_models() -> list[str]:
    """Lista todos os modelos disponíveis no Ollama."""
    try:
        # Cria um cliente HTTP assíncrono com timeout de 5 segundos
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Faz uma requisição GET para o endpoint de tags
            resp = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            # Lança exceção se o status não for 2xx
            resp.raise_for_status()
            # Decodifica a resposta JSON
            data = resp.json()
            # Extrai e retorna uma lista com os nomes dos modelos
            return [m["name"] for m in data.get("models", [])]
    except Exception as e:
        # Em caso de erro, registra um aviso e retorna lista vazia
        logger.warning(f"Não foi possível listar modelos do Ollama: {e}")
        return []


def normalize_ollama_model(model_name: str) -> str:
    """Remove o prefixo 'ollama/' do nome do modelo se presente."""
    # Se o nome começa com "ollama/", remove esse prefixo
    if model_name.startswith("ollama/"):
        return model_name[len("ollama/"):]
    # Caso contrário, retorna o nome sem alteração
    return model_name


def _extract_ollama_image_data(block: dict) -> str | None:
    """Extrai dados de imagem base64 de um bloco de conteúdo da API Anthropic."""
    # Obtém o campo 'source' do bloco
    source = block.get("source")
    # Verifica se source é um dicionário
    if not isinstance(source, dict):
        return None
    # Verifica se o tipo é base64
    if source.get("type") != "base64":
        return None
    # Obtém os dados da imagem
    data = source.get("data")
    # Retorna os dados se for uma string não vazia
    if isinstance(data, str) and data:
        return data
    return None


def anthropic_to_ollama_messages(messages: list[dict]) -> list[dict]:
    """Converte mensagens do formato Anthropic para o formato Ollama."""
    ollama_messages = []  # Lista de mensagens convertidas
    # Itera sobre cada mensagem de entrada
    for msg in messages:
        role = msg.get("role", "user")     # Obtém o papel (user, assistant, etc.)
        content = msg.get("content", "")   # Obtém o conteúdo da mensagem
        # Se o conteúdo é uma string simples, adiciona diretamente
        if isinstance(content, str):
            ollama_messages.append({"role": role, "content": content})
        # Se o conteúdo é uma lista de blocos (texto, imagem, etc.)
        elif isinstance(content, list):
            text_parts = []   # Partes de texto extraídas
            image_parts = []  # Dados de imagens extraídos (base64)
            # Itera sobre cada bloco do conteúdo
            for block in content:
                if isinstance(block, dict):
                    # Se é um bloco de texto, extrai o texto
                    if block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
                    # Se é um bloco de imagem, tenta extrair os dados base64
                    elif block.get("type") == "image":
                        image_data = _extract_ollama_image_data(block)
                        if image_data:
                            image_parts.append(image_data)
                        else:
                            # Se não conseguiu extrair, adiciona placeholder [image]
                            text_parts.append("[image]")
                # Se o bloco é uma string direta, adiciona ao texto
                elif isinstance(block, str):
                    text_parts.append(block)
            # Monta a mensagem Ollama com as partes de texto unidas por quebra de linha
            ollama_message = {"role": role, "content": "\n".join(text_parts)}
            # Se há imagens, adiciona o campo images à mensagem
            if image_parts:
                ollama_message["images"] = image_parts
            ollama_messages.append(ollama_message)
    # Retorna a lista de mensagens convertidas
    return ollama_messages


async def ollama_chat(
    model: str,                      # Nome/ID do modelo a ser usado
    messages: list[dict],            # Lista de mensagens da conversa
    system: str | None = None,       # Prompt de sistema opcional
    max_tokens: int = 4096,          # Número máximo de tokens na resposta
    temperature: float = 1.0,        # Temperatura para controle de aleatoriedade
) -> dict:
    """Envia uma requisição de chat para o Ollama (sem streaming) e retorna a resposta formatada."""
    # Normaliza o nome do modelo (remove prefixo ollama/ se presente)
    model = normalize_ollama_model(model)
    # Converte as mensagens do formato Anthropic para o formato Ollama
    ollama_messages = anthropic_to_ollama_messages(messages)
    # Insere o prompt de sistema como primeira mensagem se fornecido
    if system:
        ollama_messages.insert(0, {"role": "system", "content": system})
    # Monta o payload da requisição
    payload = {
        "model": model,               # Modelo a ser usado
        "messages": ollama_messages,   # Mensagens convertidas
        "stream": False,               # Sem streaming
        "options": {"num_predict": max_tokens, "temperature": temperature},  # Opções de geração
    }
    # Faz a requisição POST para a API de chat do Ollama
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload)
        resp.raise_for_status()  # Lança exceção se status não for 2xx
        data = resp.json()       # Decodifica a resposta JSON
    # Extrai o texto da resposta do assistente
    assistant_text = data.get("message", {}).get("content", "")
    # Retorna a resposta no formato compatível com a API da Anthropic
    return {
        "id": f"msg_ollama_{data.get('created_at', 'unknown')}",  # ID da mensagem
        "type": "message",                                          # Tipo do objeto
        "role": "assistant",                                        # Papel (assistente)
        "content": [{"type": "text", "text": assistant_text}],      # Conteúdo da resposta
        "model": model,                                              # Modelo utilizado
        "stop_reason": "end_turn",                                   # Razão de parada
        "stop_sequence": None,                                       # Sequência de parada (nenhuma)
        "usage": {
            "input_tokens": data.get("prompt_eval_count", 0),        # Tokens de entrada (avaliação do prompt)
            "output_tokens": data.get("eval_count", 0),              # Tokens de saída (avaliação da resposta)
        },
    }


async def ollama_chat_stream(
    model: str,                      # Nome/ID do modelo a ser usado
    messages: list[dict],            # Lista de mensagens da conversa
    system: str | None = None,       # Prompt de sistema opcional
    max_tokens: int = 4096,          # Número máximo de tokens na resposta
    temperature: float = 1.0,        # Temperatura para controle de aleatoriedade
) -> AsyncIterator[str]:
    """Envia uma requisição de chat com streaming e retorna eventos SSE no formato Anthropic."""
    # Importa json aqui para uso local
    import json
    # Normaliza o nome do modelo
    model = normalize_ollama_model(model)
    # Converte as mensagens para o formato Ollama
    ollama_messages = anthropic_to_ollama_messages(messages)
    # Insere o prompt de sistema se fornecido
    if system:
        ollama_messages.insert(0, {"role": "system", "content": system})
    # Monta o payload com streaming habilitado
    payload = {
        "model": model,
        "messages": ollama_messages,
        "stream": True,              # Habilita streaming
        "options": {"num_predict": max_tokens, "temperature": temperature},
    }
    # Emite o evento de início da mensagem no formato SSE
    yield "event: message_start\n"
    yield f'data: {json.dumps({"type": "message_start", "message": {"id": "msg_ollama_stream", "type": "message", "role": "assistant", "content": [], "model": model, "stop_reason": None, "usage": {"input_tokens": 0, "output_tokens": 0}}})}\n\n'
    # Emite o evento de início do bloco de conteúdo
    yield "event: content_block_start\n"
    yield f'data: {json.dumps({"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}})}\n\n'
    # Faz a requisição POST com streaming
    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream("POST", f"{OLLAMA_BASE_URL}/api/chat", json=payload) as resp:
            resp.raise_for_status()  # Verifica se o status é OK
            # Itera sobre cada linha da resposta stream
            async for line in resp.aiter_lines():
                # Ignora linhas vazias
                if not line:
                    continue
                try:
                    # Decodifica o chunk JSON (cada linha é um objeto JSON completo)
                    chunk = json.loads(line)
                    # Extrai o texto incremental da resposta
                    delta_text = chunk.get("message", {}).get("content", "")
                    # Se há texto novo, emite um evento de delta de conteúdo
                    if delta_text:
                        yield "event: content_block_delta\n"
                        yield f'data: {json.dumps({"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": delta_text}})}\n\n'
                    # Verifica se o streaming terminou (campo "done" é True)
                    if chunk.get("done"):
                        # Emite eventos de finalização
                        yield "event: content_block_stop\n"
                        yield f'data: {json.dumps({"type": "content_block_stop", "index": 0})}\n\n'
                        yield "event: message_delta\n"
                        yield f'data: {json.dumps({"type": "message_delta", "delta": {"stop_reason": "end_turn", "stop_sequence": None}, "usage": {"output_tokens": chunk.get("eval_count", 0)}})}\n\n'
                        yield "event: message_stop\n"
                        yield f'data: {json.dumps({"type": "message_stop"})}\n\n'
                        break  # Sai do loop de streaming
                except json.JSONDecodeError:
                    # Ignora linhas com JSON malformado
                    continue
