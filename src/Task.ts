// Importa a função randomInt do módulo crypto para gerar números aleatórios seguros
import { randomInt } from 'crypto'
// Importa o tipo de estado da aplicação
import type { AppState } from './state/AppState.js'
// Importa o tipo de identificador de agente
import type { AgentId } from './types/ids.js'
// Importa a função que retorna o caminho de saída para uma tarefa
import { getTaskOutputPath } from './utils/task/diskOutput.js'

// Define os tipos possíveis de tarefa no sistema
export type TaskType =
  | 'local_bash'            // Comando bash local
  | 'local_agent'           // Agente local
  | 'remote_agent'          // Agente remoto
  | 'in_process_teammate'   // Colega de equipe no mesmo processo
  | 'local_workflow'        // Fluxo de trabalho local
  | 'monitor_mcp'           // Monitor MCP (Model Context Protocol)
  | 'dream'                 // Tarefa de sonho/planejamento

// Define os status possíveis de uma tarefa
export type TaskStatus =
  | 'pending'    // Pendente - aguardando execução
  | 'running'    // Executando
  | 'completed'  // Concluída com sucesso
  | 'failed'     // Falhou
  | 'killed'     // Encerrada/morta

/**
 * Retorna verdadeiro quando uma tarefa está em estado terminal e não fará mais transições.
 * Usado para impedir injeção de mensagens em colegas de equipe mortos, despejar
 * tarefas finalizadas do AppState e caminhos de limpeza de órfãos.
 */
export function isTerminalTaskStatus(status: TaskStatus): boolean {
  // Verifica se o status é completado, falhou ou foi morto
  return status === 'completed' || status === 'failed' || status === 'killed'
}

// Tipo que representa um handle (referência) para uma tarefa
export type TaskHandle = {
  taskId: string           // ID único da tarefa
  cleanup?: () => void     // Função opcional de limpeza
}

// Tipo para a função que atualiza o estado da aplicação (padrão setter funcional)
export type SetAppState = (f: (prev: AppState) => AppState) => void

// Tipo que agrupa o contexto necessário para executar uma tarefa
export type TaskContext = {
  abortController: AbortController    // Controlador para cancelar a tarefa
  getAppState: () => AppState         // Getter do estado atual da aplicação
  setAppState: SetAppState            // Setter do estado da aplicação
}

// Campos base compartilhados por todos os estados de tarefa
export type TaskStateBase = {
  id: string               // ID único da tarefa
  type: TaskType           // Tipo da tarefa
  status: TaskStatus       // Status atual da tarefa
  description: string      // Descrição legível da tarefa
  toolUseId?: string       // ID de uso da ferramenta (opcional)
  startTime: number        // Timestamp de início
  endTime?: number         // Timestamp de fim (opcional, preenchido ao finalizar)
  totalPausedMs?: number   // Total de milissegundos pausado (opcional)
  outputFile: string       // Caminho do arquivo de saída
  outputOffset: number     // Offset de leitura do arquivo de saída
  notified: boolean        // Se o usuário já foi notificado
}

// Tipo de entrada para spawnar um shell local
export type LocalShellSpawnInput = {
  command: string          // Comando a ser executado
  description: string      // Descrição do comando
  timeout?: number         // Timeout em milissegundos (opcional)
  toolUseId?: string       // ID de uso da ferramenta (opcional)
  agentId?: AgentId        // ID do agente que solicitou (opcional)
  /** Variante de exibição na UI: descrição como rótulo, título de diálogo, pílula da barra de status. */
  kind?: 'bash' | 'monitor' // Tipo de exibição na interface
}

// Tipo da interface Task que define o contrato para implementações de tarefas.
// O que getTaskByType despacha: kill. spawn/render nunca foram
// chamados polimorficamente (removidos em #22546). Todas as seis implementações de kill
// usam apenas setAppState — getAppState/abortController eram peso morto.
export type Task = {
  name: string             // Nome legível da tarefa
  type: TaskType           // Tipo da tarefa
  kill(taskId: string, setAppState: SetAppState): Promise<void> // Método para matar a tarefa
}

// Mapeamento de prefixos de ID por tipo de tarefa
const TASK_ID_PREFIXES: Record<string, string> = {
  local_bash: 'b',              // 'b' para bash (mantido para compatibilidade)
  local_agent: 'a',             // 'a' para agente local
  remote_agent: 'r',            // 'r' para agente remoto
  in_process_teammate: 't',     // 't' para colega de equipe
  local_workflow: 'w',          // 'w' para workflow
  monitor_mcp: 'm',             // 'm' para monitor MCP
  dream: 'd',                   // 'd' para dream
}

// Retorna o prefixo do ID de tarefa com base no tipo
function getTaskIdPrefix(type: TaskType): string {
  // Busca o prefixo no mapeamento, ou retorna 'x' como fallback
  return TASK_ID_PREFIXES[type] ?? 'x'
}

// Alfabeto seguro para IDs de tarefa (dígitos + letras minúsculas), case-insensitive.
// 36^8 ≈ 2.8 trilhões de combinações, suficiente para resistir a ataques de força bruta com symlinks.
const TASK_ID_ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyz'

// Gera um ID único para uma tarefa com prefixo baseado no tipo
export function generateTaskId(type: TaskType): string {
  const prefix = getTaskIdPrefix(type) // Obtém o prefixo do tipo
  let id = prefix // Inicializa o ID com o prefixo
  // Gera 8 caracteres aleatórios usando o alfabeto seguro
  for (let i = 0; i < 8; i++) {
    id += TASK_ID_ALPHABET[randomInt(TASK_ID_ALPHABET.length)]!
  }
  return id // Retorna o ID gerado (ex: "b3f7x9k2a")
}

// Cria o estado base de uma tarefa com valores iniciais
export function createTaskStateBase(
  id: string,              // ID da tarefa
  type: TaskType,          // Tipo da tarefa
  description: string,     // Descrição da tarefa
  toolUseId?: string,      // ID de uso da ferramenta (opcional)
): TaskStateBase {
  return {
    id,                                    // ID da tarefa
    type,                                  // Tipo da tarefa
    status: 'pending',                     // Status inicial: pendente
    description,                           // Descrição da tarefa
    toolUseId,                             // ID de uso da ferramenta
    startTime: Date.now(),                 // Timestamp atual como hora de início
    outputFile: getTaskOutputPath(id),     // Calcula o caminho do arquivo de saída
    outputOffset: 0,                       // Offset de saída começa em 0
    notified: false,                       // Ainda não foi notificado
  }
}
