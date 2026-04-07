"""
smart_router.py
---------------
Roteador inteligente automático para o openclaude.

Em vez de sempre usar um provedor fixo, o roteador inteligente:
- Pinga todos os provedores configurados na inicialização
- Pontua-os por latência, custo e saúde
- Roteia cada requisição para o provedor ideal
- Faz fallback automático se um provedor falhar
- Aprende com os tempos reais de requisição ao longo do tempo

Uso em server.py:
    from smart_router import SmartRouter
    router = SmartRouter()
    await router.initialize()
    result = await router.route(messages, model, stream)

Configuração .env:
    ROUTER_MODE=smart          # ou: fixed (comportamento padrão)
    ROUTER_STRATEGY=latency    # ou: cost, balanced
    ROUTER_FALLBACK=true       # auto-retry em caso de falha

Contribuição para: https://github.com/Gitlawb/openclaude
"""

# Importa asyncio para operações assíncronas (gather, sleep, tarefas)
import asyncio
# Importa logging para registro de logs
import logging
# Importa os para acessar variáveis de ambiente
import os
# Importa time para medir latência com precisão
import time
# Importa dataclass para criar classes de dados e field para campos com valores padrão
from dataclasses import dataclass, field
# Importa Optional para tipar parâmetros opcionais
from typing import Optional
# Importa httpx para requisições HTTP assíncronas
import httpx

# Cria um logger com o nome do módulo atual
logger = logging.getLogger(__name__)

# ── Definições de provedores ──────────────────────────────────────────────────────

@dataclass
class Provider:
    """Classe de dados que representa um provedor de LLM com métricas de saúde e performance."""
    name: str                        # Nome do provedor (ex: "openai", "gemini", "ollama")
    ping_url: str                    # URL usada para verificar a saúde do provedor
    api_key_env: str                 # Nome da variável de ambiente da API key
    cost_per_1k_tokens: float        # Custo estimado em USD por 1k tokens
    big_model: str                   # Modelo para requisições grandes (sonnet/large)
    small_model: str                 # Modelo para requisições pequenas (haiku/small)
    latency_ms: float = 9999.0       # Latência em ms (atualizada pelo benchmark)
    healthy: bool = True             # Se o provedor está saudável (atualizado por health checks)
    request_count: int = 0           # Total de requisições roteadas para este provedor
    error_count: int = 0             # Total de erros deste provedor
    avg_latency_ms: float = 9999.0   # Média móvel de latência de requisições reais

    @property
    def api_key(self) -> Optional[str]:
        """Retorna a API key do provedor lida da variável de ambiente."""
        return os.getenv(self.api_key_env)

    @property
    def is_configured(self) -> bool:
        """Retorna True se o provedor tem uma API key configurada."""
        # Provedores locais (ollama, atomic-chat) não precisam de API key
        if self.name in ("ollama", "atomic-chat"):
            return True
        # Provedores na nuvem precisam de API key
        return bool(self.api_key)

    @property
    def error_rate(self) -> float:
        """Calcula a taxa de erros do provedor (erros / total de requisições)."""
        if self.request_count == 0:
            return 0.0
        return self.error_count / self.request_count

    def score(self, strategy: str = "balanced") -> float:
        """
        Calcula o score do provedor. Menor score = melhor provedor.
        strategy: 'latency' (baixa latência) | 'cost' (menor custo) | 'balanced' (equilibrado)
        """
        # Se não está saudável ou não está configurado, retorna infinito (nunca será selecionado)
        if not self.healthy or not self.is_configured:
            return float("inf")

        # Normaliza a latência para segundos
        latency_score = self.avg_latency_ms / 1000.0
        # Normaliza o custo para escala similar
        cost_score = self.cost_per_1k_tokens * 100
        # Penalidade pesada para taxa de erros alta
        error_penalty = self.error_rate * 500

        # Calcula o score baseado na estratégia escolhida
        if strategy == "latency":
            # Estratégia de latência: prioriza velocidade
            return latency_score + error_penalty
        elif strategy == "cost":
            # Estratégia de custo: prioriza economia
            return cost_score + error_penalty
        else:  # balanced (equilibrado)
            # Estratégia equilibrada: pondera igualmente latência e custo
            return (latency_score * 0.5) + (cost_score * 0.5) + error_penalty


# ── Catálogo padrão de provedores ────────────────────────────────────────────────

def build_default_providers() -> list[Provider]:
    """Constrói a lista padrão de provedores com base nas variáveis de ambiente."""
    # Lê os modelos grande e pequeno das variáveis de ambiente
    big = os.getenv("BIG_MODEL", "gpt-4.1")
    small = os.getenv("SMALL_MODEL", "gpt-4.1-mini")
    # Lê as URLs base dos provedores locais
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    atomic_chat_url = os.getenv("ATOMIC_CHAT_BASE_URL", "http://127.0.0.1:1337")

    # Retorna a lista de provedores padrão
    return [
        Provider(
            name="openai",                                              # Provedor OpenAI
            ping_url="https://api.openai.com/v1/models",               # Endpoint de saúde
            api_key_env="OPENAI_API_KEY",                               # Variável de ambiente da chave
            cost_per_1k_tokens=0.002,                                   # Custo por 1k tokens
            big_model=big if "gpt" in big else "gpt-4.1",              # Modelo grande (usa GPT se compatível)
            small_model=small if "gpt" in small else "gpt-4.1-mini",   # Modelo pequeno
        ),
        Provider(
            name="gemini",                                              # Provedor Google Gemini
            ping_url="https://generativelanguage.googleapis.com/v1/models",  # Endpoint de saúde
            api_key_env="GEMINI_API_KEY",                               # Variável de ambiente da chave
            cost_per_1k_tokens=0.0005,                                  # Custo por 1k tokens (mais barato)
            big_model=big if "gemini" in big else "gemini-2.5-pro",    # Modelo grande
            small_model=small if "gemini" in small else "gemini-2.0-flash",  # Modelo pequeno
        ),
        Provider(
            name="ollama",                                              # Provedor Ollama (local)
            ping_url=f"{ollama_url}/api/tags",                          # Endpoint de saúde
            api_key_env="",                                             # Sem API key (local)
            cost_per_1k_tokens=0.0,                                     # Gratuito (local)
            big_model=big if "gemini" not in big and "gpt" not in big else "llama3:8b",    # Modelo grande local
            small_model=small if "gemini" not in small and "gpt" not in small else "llama3:8b",  # Modelo pequeno local
        ),
        Provider(
            name="atomic-chat",                                         # Provedor Atomic Chat (local, Apple Silicon)
            ping_url=f"{atomic_chat_url}/v1/models",                    # Endpoint de saúde
            api_key_env="",                                             # Sem API key (local)
            cost_per_1k_tokens=0.0,                                     # Gratuito (local)
            big_model=big if "gemini" not in big and "gpt" not in big else "llama3:8b",
            small_model=small if "gemini" not in small and "gpt" not in small else "llama3:8b",
        ),
    ]


# ── Roteador Inteligente ──────────────────────────────────────────────────────

class SmartRouter:
    """
    Roteia inteligentemente requisições de API do Claude Code para o melhor
    provedor de LLM disponível com base em latência, custo e saúde.
    """

    def __init__(
        self,
        providers: Optional[list[Provider]] = None,       # Lista customizada de provedores (opcional)
        strategy: Optional[str] = None,                   # Estratégia de roteamento (opcional)
        fallback_enabled: Optional[bool] = None,          # Se o fallback está habilitado (opcional)
    ):
        # Usa provedores customizados ou os padrão
        self.providers = providers or build_default_providers()
        # Lê a estratégia da variável de ambiente ou usa "balanced" como padrão
        self.strategy = strategy or os.getenv("ROUTER_STRATEGY", "balanced")
        # Verifica se o fallback está habilitado
        self.fallback_enabled = (
            fallback_enabled
            if fallback_enabled is not None
            else os.getenv("ROUTER_FALLBACK", "true").lower() == "true"
        )
        # Flag que indica se o roteador já foi inicializado
        self._initialized = False

    # ── Inicialização ────────────────────────────────────────────────────────

    async def initialize(self) -> None:
        """Pinga todos os provedores e constrói scores iniciais de latência."""
        logger.info("SmartRouter: benchmarkando provedores...")
        # Executa pings em todos os provedores simultaneamente
        await asyncio.gather(
            *[self._ping_provider(p) for p in self.providers],
            return_exceptions=True,  # Não interrompe se um provedor falhar
        )
        # Filtra os provedores disponíveis (saudáveis e configurados)
        available = [p for p in self.providers if p.healthy and p.is_configured]
        logger.info(
            f"SmartRouter pronto. Provedores disponíveis: "
            f"{[p.name for p in available]}"
        )
        # Avisa se nenhum provedor está disponível
        if not available:
            logger.warning(
                "SmartRouter: nenhum provedor disponível! "
                "Verifique suas API keys no .env"
            )
        self._initialized = True

    async def _ping_provider(self, provider: Provider) -> None:
        """Mede a latência para o endpoint de saúde de um provedor."""
        # Se não está configurado, marca como não saudável e pula
        if not provider.is_configured:
            provider.healthy = False
            logger.debug(f"SmartRouter: {provider.name} pulado — sem API key")
            return

        # Prepara o header de autenticação se houver API key
        headers = {}
        if provider.api_key:
            headers["Authorization"] = f"Bearer {provider.api_key}"

        # Marca o tempo de início com alta precisão
        start = time.monotonic()
        try:
            # Faz requisição GET com timeout de 5 segundos
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(provider.ping_url, headers=headers)
                # Calcula o tempo decorrido em milissegundos
                elapsed_ms = (time.monotonic() - start) * 1000
                # Status 200/400/401/403 significa que o endpoint é acessível
                if resp.status_code in (200, 400, 401, 403):
                    # 400/401/403 significa acessível, possivelmente chave inválida
                    # Ainda marca como saudável para fins de roteamento
                    provider.healthy = True
                    provider.latency_ms = elapsed_ms
                    provider.avg_latency_ms = elapsed_ms
                    logger.info(
                        f"SmartRouter: {provider.name} OK "
                        f"({elapsed_ms:.0f}ms, status={resp.status_code})"
                    )
                else:
                    # Outros status indicam problema
                    provider.healthy = False
                    logger.warning(
                        f"SmartRouter: {provider.name} não saudável "
                        f"(status={resp.status_code})"
                    )
        except Exception as e:
            # Exceção indica que o provedor é inacessível
            provider.healthy = False
            logger.warning(f"SmartRouter: {provider.name} inacessível — {e}")

    # ── Lógica de roteamento ─────────────────────────────────────────────────────────

    def select_provider(self, is_large_request: bool = False) -> Optional[Provider]:
        """
        Seleciona o melhor provedor disponível para esta requisição.
        Retorna None se nenhum provedor está disponível.
        """
        # Filtra provedores que estão saudáveis e configurados
        available = [
            p for p in self.providers
            if p.healthy and p.is_configured
        ]
        if not available:
            return None

        # Retorna o provedor com menor score (melhor)
        return min(available, key=lambda p: p.score(self.strategy))

    def get_model_for_provider(
        self,
        provider: Provider,        # Provedor selecionado
        claude_model: str,          # Nome do modelo Claude solicitado
        is_large_request: bool = False,  # Se é uma requisição grande
    ) -> str:
        """Mapeia um nome de modelo Claude para o modelo real do provedor."""
        # Se a requisição é grande, usa o modelo grande
        if is_large_request:
            return provider.big_model
        # Verifica se o nome do modelo contém palavras-chave de modelos grandes
        is_large = any(
            keyword in claude_model.lower()
            for keyword in ["opus", "sonnet", "large", "big"]
        )
        # Retorna modelo grande ou pequeno baseado na classificação
        return provider.big_model if is_large else provider.small_model

    def is_large_request(self, messages: list[dict]) -> bool:
        """Estima se esta é uma requisição grande baseada no tamanho das mensagens."""
        # Soma o total de caracteres de todas as mensagens
        total_chars = sum(
            len(str(m.get("content", ""))) for m in messages
        )
        # Mais de 2000 caracteres = trata como requisição grande
        return total_chars > 2000

    def _update_latency(self, provider: Provider, duration_ms: float) -> None:
        """Atualização de média móvel exponencial para rastreamento de latência."""
        alpha = 0.3  # Peso para nova observação (30% novo, 70% histórico)
        provider.avg_latency_ms = (
            alpha * duration_ms + (1 - alpha) * provider.avg_latency_ms
        )

    # ── Ponto de entrada principal de roteamento ──────────────────────────────────

    async def route(
        self,
        messages: list[dict],                              # Mensagens da conversa
        claude_model: str = "claude-sonnet",               # Modelo Claude solicitado
        attempt: int = 0,                                  # Número da tentativa (para fallback)
        exclude_providers: Optional[list[str]] = None,     # Provedores a excluir
    ) -> dict:
        """
        Roteia uma requisição para o melhor provedor.
        Retorna um dict com informações da decisão de roteamento:
          {
            "provider": nome do provedor,
            "model": modelo real a usar,
            "api_key": API key do provedor,
            "base_url": URL base do provedor,
          }
        Lança RuntimeError se nenhum provedor disponível.
        """
        # Inicializa se ainda não foi feito
        if not self._initialized:
            await self.initialize()

        # Cria conjunto de provedores a excluir
        exclude = set(exclude_providers or [])
        # Verifica se é uma requisição grande
        large = self.is_large_request(messages)

        # Filtra provedores disponíveis excluindo os da lista de exclusão
        available = [
            p for p in self.providers
            if p.healthy and p.is_configured and p.name not in exclude
        ]

        # Se não há provedores disponíveis, lança erro
        if not available:
            raise RuntimeError(
                "SmartRouter: nenhum provedor disponível. "
                "Verifique suas API keys e a saúde dos provedores."
            )

        # Seleciona o provedor com menor score (melhor)
        provider = min(available, key=lambda p: p.score(self.strategy))
        # Obtém o modelo real para o provedor selecionado
        model = self.get_model_for_provider(
            provider,
            claude_model,
            is_large_request=large,
        )

        # Registra a decisão de roteamento para debug
        logger.debug(
            f"SmartRouter: roteando para {provider.name}/{model} "
            f"(strategy={self.strategy}, large={large}, attempt={attempt})"
        )

        # Retorna a decisão de roteamento
        return {
            "provider": provider.name,             # Nome do provedor selecionado
            "model": model,                        # Modelo real a ser usado
            "api_key": provider.api_key or "none", # API key (ou "none" para locais)
            "provider_object": provider,           # Referência ao objeto provedor
        }

    async def record_result(
        self,
        provider_name: str,       # Nome do provedor que processou a requisição
        success: bool,            # Se a requisição foi bem-sucedida
        duration_ms: float,       # Duração da requisição em milissegundos
    ) -> None:
        """
        Registra o resultado de uma requisição.
        Chamado após cada requisição proxied para atualizar os scores dos provedores.
        """
        # Busca o provedor pelo nome
        provider = next(
            (p for p in self.providers if p.name == provider_name), None
        )
        if not provider:
            return  # Provedor não encontrado, ignora

        # Incrementa o contador de requisições
        provider.request_count += 1
        if success:
            # Se sucesso, atualiza a média de latência
            self._update_latency(provider, duration_ms)
        else:
            # Se falha, incrementa o contador de erros
            provider.error_count += 1
            # Após 3+ requisições com taxa de erros > 70%, marca como não saudável
            recent_errors = provider.error_count
            recent_total = provider.request_count
            if recent_total >= 3 and (recent_errors / recent_total) > 0.7:
                logger.warning(
                    f"SmartRouter: taxa de erros de {provider_name} alta "
                    f"({provider.error_rate:.0%}), marcando como não saudável"
                )
                provider.healthy = False
                # Agenda uma re-verificação após 60 segundos
                asyncio.create_task(self._recheck_provider(provider, delay=60))

    async def _recheck_provider(
        self, provider: Provider, delay: float = 60
    ) -> None:
        """Re-pinga um provedor após um atraso e restaura se estiver saudável."""
        # Aguarda o tempo especificado antes de re-verificar
        await asyncio.sleep(delay)
        # Pinga o provedor novamente
        await self._ping_provider(provider)
        # Se o provedor se recuperou, registra no log
        if provider.healthy:
            logger.info(
                f"SmartRouter: {provider.name} recuperado, "
                f"re-adicionando ao pool"
            )

    # ── Relatório de status ─────────────────────────────────────────────────────────

    def status(self) -> list[dict]:
        """Retorna o status atual dos provedores para monitoramento."""
        return [
            {
                "provider": p.name,                                    # Nome do provedor
                "healthy": p.healthy,                                  # Se está saudável
                "configured": p.is_configured,                         # Se está configurado
                "latency_ms": round(p.avg_latency_ms, 1),              # Latência média em ms
                "cost_per_1k": p.cost_per_1k_tokens,                   # Custo por 1k tokens
                "requests": p.request_count,                           # Total de requisições
                "errors": p.error_count,                               # Total de erros
                "error_rate": f"{p.error_rate:.1%}",                   # Taxa de erros formatada
                "score": round(p.score(self.strategy), 3)              # Score calculado
                if p.healthy and p.is_configured
                else "N/A",                                            # "N/A" se não disponível
            }
            for p in self.providers  # Itera sobre todos os provedores
        ]
