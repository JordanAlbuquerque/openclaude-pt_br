// Importa a flag de feature do bundler Bun para habilitar/desabilitar funcionalidades condicionalmente
import { feature } from 'bun:bundle'
// Importa a função memoize do lodash para cache de resultados de funções
import memoize from 'lodash-es/memoize.js'
// Importa funções para obter diretórios adicionais do CLAUDE.md e armazenar conteúdo em cache
import {
  getAdditionalDirectoriesForClaudeMd,
  setCachedClaudeMdContent,
} from './bootstrap/state.js'
// Importa a função que retorna a data local em formato ISO
import { getLocalISODate } from './constants/common.js'
// Importa funções para filtrar arquivos de memória e obter conteúdo do CLAUDE.md
import {
  filterInjectedMemoryFiles,
  getClaudeMds,
  getMemoryFiles,
} from './utils/claudemd.js'
// Importa a função de logging para diagnósticos sem informações pessoais identificáveis
import { logForDiagnosticsNoPII } from './utils/diagLogs.js'
// Importa utilitários para verificar modo "bare" e variáveis de ambiente truthy
import { isBareMode, isEnvTruthy } from './utils/envUtils.js'
// Importa função para executar arquivos sem lançar exceções
import { execFileNoThrow } from './utils/execFileNoThrow.js'
// Importa funções utilitárias do git: obter branch, branch padrão, verificar se é repo git, e caminho do executável git
import { getBranch, getDefaultBranch, getIsGit, gitExe } from './utils/git.js'
// Importa função que verifica se instruções git devem ser incluídas
import { shouldIncludeGitInstructions } from './utils/gitSettings.js'
// Importa função de logging de erros
import { logError } from './utils/log.js'

// Limite máximo de caracteres para a saída do git status
const MAX_STATUS_CHARS = 2000

// Injeção de prompt no sistema para quebra de cache (apenas interno, estado de depuração efêmero)
let systemPromptInjection: string | null = null

// Retorna o valor atual da injeção de prompt do sistema
export function getSystemPromptInjection(): string | null {
  return systemPromptInjection
}

// Define o valor da injeção de prompt do sistema e limpa os caches de contexto
export function setSystemPromptInjection(value: string | null): void {
  systemPromptInjection = value
  // Limpa os caches de contexto imediatamente quando a injeção muda
  getUserContext.cache.clear?.()
  getSystemContext.cache.clear?.()
}

// Função memoizada que obtém o status do git (executa apenas uma vez e armazena em cache)
export const getGitStatus = memoize(async (): Promise<string | null> => {
  // Em ambiente de teste, retorna null para evitar ciclos
  if (process.env.NODE_ENV === 'test') {
    return null
  }

  // Marca o tempo de início para métricas de performance
  const startTime = Date.now()
  logForDiagnosticsNoPII('info', 'git_status_started')

  // Verifica se o diretório atual é um repositório git
  const isGitStart = Date.now()
  const isGit = await getIsGit()
  logForDiagnosticsNoPII('info', 'git_is_git_check_completed', {
    duration_ms: Date.now() - isGitStart,
    is_git: isGit,
  })

  // Se não é um repositório git, retorna null
  if (!isGit) {
    logForDiagnosticsNoPII('info', 'git_status_skipped_not_git', {
      duration_ms: Date.now() - startTime,
    })
    return null
  }

  try {
    // Executa múltiplos comandos git em paralelo para melhor performance
    const gitCmdsStart = Date.now()
    const [branch, mainBranch, status, log, userName] = await Promise.all([
      getBranch(),          // Obtém a branch atual
      getDefaultBranch(),   // Obtém a branch padrão (main/master)
      // Obtém o status resumido do git (arquivos modificados, staged, etc.)
      execFileNoThrow(gitExe(), ['--no-optional-locks', 'status', '--short'], {
        preserveOutputOnError: false,
      }).then(({ stdout }) => stdout.trim()),
      // Obtém os últimos 5 commits em formato de uma linha
      execFileNoThrow(
        gitExe(),
        ['--no-optional-locks', 'log', '--oneline', '-n', '5'],
        {
          preserveOutputOnError: false,
        },
      ).then(({ stdout }) => stdout.trim()),
      // Obtém o nome do usuário git configurado
      execFileNoThrow(gitExe(), ['config', 'user.name'], {
        preserveOutputOnError: false,
      }).then(({ stdout }) => stdout.trim()),
    ])

    // Registra a conclusão dos comandos git
    logForDiagnosticsNoPII('info', 'git_commands_completed', {
      duration_ms: Date.now() - gitCmdsStart,
      status_length: status.length,
    })

    // Verifica se o status excede o limite de caracteres e trunca se necessário
    const truncatedStatus =
      status.length > MAX_STATUS_CHARS
        ? status.substring(0, MAX_STATUS_CHARS) +
          '\n... (truncated because it exceeds 2k characters. If you need more information, run "git status" using BashTool)'
        : status

    // Registra a conclusão do status git
    logForDiagnosticsNoPII('info', 'git_status_completed', {
      duration_ms: Date.now() - startTime,
      truncated: status.length > MAX_STATUS_CHARS,
    })

    // Monta e retorna a string formatada com informações do git
    return [
      `This is the git status at the start of the conversation. Note that this status is a snapshot in time, and will not update during the conversation.`,
      `Current branch: ${branch}`,                                      // Branch atual
      `Main branch (you will usually use this for PRs): ${mainBranch}`, // Branch principal para PRs
      ...(userName ? [`Git user: ${userName}`] : []),                    // Nome do usuário git (se disponível)
      `Status:\n${truncatedStatus || '(clean)'}`,                       // Status do repositório
      `Recent commits:\n${log}`,                                        // Commits recentes
    ].join('\n\n')
  } catch (error) {
    // Em caso de erro, registra e retorna null
    logForDiagnosticsNoPII('error', 'git_status_failed', {
      duration_ms: Date.now() - startTime,
    })
    logError(error)
    return null
  }
})

/**
 * Este contexto é prefixado a cada conversa e armazenado em cache durante toda a conversa.
 * Contém informações do sistema como status do git e injeções de cache.
 */
export const getSystemContext = memoize(
  async (): Promise<{
    [k: string]: string
  }> => {
    const startTime = Date.now()
    logForDiagnosticsNoPII('info', 'system_context_started')

    // Pula o status do git no CCR (overhead desnecessário ao retomar) ou quando instruções git estão desabilitadas
    const gitStatus =
      isEnvTruthy(process.env.CLAUDE_CODE_REMOTE) ||
      !shouldIncludeGitInstructions()
        ? null
        : await getGitStatus()

    // Inclui injeção de prompt do sistema se definida (para quebra de cache, apenas interno)
    const injection = feature('BREAK_CACHE_COMMAND')
      ? getSystemPromptInjection()
      : null

    // Registra a conclusão do contexto do sistema
    logForDiagnosticsNoPII('info', 'system_context_completed', {
      duration_ms: Date.now() - startTime,
      has_git_status: gitStatus !== null,
      has_injection: injection !== null,
    })

    // Retorna o contexto do sistema com status git e quebra de cache (se aplicável)
    return {
      ...(gitStatus && { gitStatus }),                          // Inclui status git se disponível
      ...(feature('BREAK_CACHE_COMMAND') && injection           // Inclui quebrador de cache se feature habilitada e injeção presente
        ? {
            cacheBreaker: `[CACHE_BREAKER: ${injection}]`,
          }
        : {}),
    }
  },
)

/**
 * Este contexto é prefixado a cada conversa e armazenado em cache durante toda a conversa.
 * Contém informações do usuário como conteúdo do CLAUDE.md e data atual.
 */
export const getUserContext = memoize(
  async (): Promise<{
    [k: string]: string
  }> => {
    const startTime = Date.now()
    logForDiagnosticsNoPII('info', 'user_context_started')

    // CLAUDE_CODE_DISABLE_CLAUDE_MDS: desabilita completamente, sempre.
    // --bare: pula auto-descoberta (caminhamento de cwd), MAS respeita --add-dir explícito.
    // --bare significa "pule o que eu não pedi", não "ignore o que eu pedi".
    const shouldDisableClaudeMd =
      isEnvTruthy(process.env.CLAUDE_CODE_DISABLE_CLAUDE_MDS) ||
      (isBareMode() && getAdditionalDirectoriesForClaudeMd().length === 0)
    // Aguarda a E/S assíncrona (readFile/readdir caminhamento de diretório) para que o event
    // loop ceda naturalmente no primeiro fs.readFile.
    const claudeMd = shouldDisableClaudeMd
      ? null
      : getClaudeMds(filterInjectedMemoryFiles(await getMemoryFiles()))
    // Cache para o classificador de modo automático (yoloClassifier.ts lê isso
    // em vez de importar claudemd.ts diretamente, o que criaria um
    // ciclo através de permissions/filesystem → permissions → yoloClassifier).
    setCachedClaudeMdContent(claudeMd || null)

    // Registra a conclusão do contexto do usuário
    logForDiagnosticsNoPII('info', 'user_context_completed', {
      duration_ms: Date.now() - startTime,
      claudemd_length: claudeMd?.length ?? 0,
      claudemd_disabled: Boolean(shouldDisableClaudeMd),
    })

    // Retorna o contexto do usuário com conteúdo do CLAUDE.md e data atual
    return {
      ...(claudeMd && { claudeMd }),                                // Inclui conteúdo do CLAUDE.md se disponível
      currentDate: `Today's date is ${getLocalISODate()}.`,         // Data atual em formato ISO local
    }
  },
)
