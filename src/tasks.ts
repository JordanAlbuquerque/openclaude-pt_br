// Importa a flag de feature do bundler Bun para habilitar/desabilitar funcionalidades condicionalmente
import { feature } from 'bun:bundle'
// Importa os tipos Task (interface de tarefa) e TaskType (tipo de tarefa)
import type { Task, TaskType } from './Task.js'
// Importa a implementação da tarefa de sonho/planejamento
import { DreamTask } from './tasks/DreamTask/DreamTask.js'
// Importa a implementação da tarefa de agente local
import { LocalAgentTask } from './tasks/LocalAgentTask/LocalAgentTask.js'
// Importa a implementação da tarefa de shell local (execução de comandos bash)
import { LocalShellTask } from './tasks/LocalShellTask/LocalShellTask.js'
// Importa a implementação da tarefa de agente remoto
import { RemoteAgentTask } from './tasks/RemoteAgentTask/RemoteAgentTask.js'

/* eslint-disable @typescript-eslint/no-require-imports */
// Carrega condicionalmente a tarefa de workflow local se a feature WORKFLOW_SCRIPTS estiver habilitada
const LocalWorkflowTask: Task | null = feature('WORKFLOW_SCRIPTS')
  ? require('./tasks/LocalWorkflowTask/LocalWorkflowTask.js').LocalWorkflowTask
  : null
// Carrega condicionalmente a tarefa de monitor MCP se a feature MONITOR_TOOL estiver habilitada
const MonitorMcpTask: Task | null = feature('MONITOR_TOOL')
  ? require('./tasks/MonitorMcpTask/MonitorMcpTask.js').MonitorMcpTask
  : null
/* eslint-enable @typescript-eslint/no-require-imports */

/**
 * Obtém todas as tarefas disponíveis.
 * Espelha o padrão do tools.ts
 * Nota: Retorna array inline para evitar problemas de dependência circular com const de nível superior
 */
export function getAllTasks(): Task[] {
  // Inicializa o array com as tarefas que sempre estão disponíveis
  const tasks: Task[] = [
    LocalShellTask,    // Tarefa de execução de shell local
    LocalAgentTask,    // Tarefa de agente local
    RemoteAgentTask,   // Tarefa de agente remoto
    DreamTask,         // Tarefa de sonho/planejamento
  ]
  // Adiciona a tarefa de workflow local se estiver disponível
  if (LocalWorkflowTask) tasks.push(LocalWorkflowTask)
  // Adiciona a tarefa de monitor MCP se estiver disponível
  if (MonitorMcpTask) tasks.push(MonitorMcpTask)
  // Retorna a lista completa de tarefas disponíveis
  return tasks
}

/**
 * Obtém uma tarefa pelo seu tipo.
 */
export function getTaskByType(type: TaskType): Task | undefined {
  // Busca na lista de todas as tarefas aquela cujo tipo corresponde ao solicitado
  return getAllTasks().find(t => t.type === type)
}
