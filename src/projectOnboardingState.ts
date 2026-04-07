// Importa a função memoize do lodash para cache de resultados de funções
import memoize from 'lodash-es/memoize.js'
// Importa a função join para construir caminhos de arquivo
import { join } from 'path'
// Importa funções para ler e salvar configuração do projeto atual
import {
  getCurrentProjectConfig,
  saveCurrentProjectConfig,
} from './utils/config.js'
// Importa a função que retorna o diretório de trabalho atual
import { getCwd } from './utils/cwd.js'
// Importa a função que verifica se um diretório está vazio
import { isDirEmpty } from './utils/file.js'
// Importa a implementação do sistema de arquivos (pode ser real ou mock)
import { getFsImplementation } from './utils/fsOperations.js'

// Tipo que representa um passo do onboarding do projeto
export type Step = {
  key: string           // Chave identificadora do passo
  text: string          // Texto descritivo do passo
  isComplete: boolean   // Se o passo já foi concluído
  isCompletable: boolean // Se o passo pode ser concluído pelo usuário
  isEnabled: boolean    // Se o passo está habilitado no contexto atual
}

// Retorna a lista de passos de onboarding do projeto
export function getSteps(): Step[] {
  // Verifica se o arquivo CLAUDE.md existe no diretório de trabalho atual
  const hasClaudeMd = getFsImplementation().existsSync(
    join(getCwd(), 'CLAUDE.md'),
  )
  // Verifica se o diretório de trabalho está vazio (sem arquivos/pastas)
  const isWorkspaceDirEmpty = isDirEmpty(getCwd())

  // Retorna os passos de onboarding
  return [
    {
      key: 'workspace',
      text: 'Ask Claude to create a new app or clone a repository', // Pedir ao Claude para criar um novo app ou clonar um repositório
      isComplete: false,         // Nunca marcado como completo diretamente
      isCompletable: true,       // Pode ser completado
      isEnabled: isWorkspaceDirEmpty, // Habilitado apenas se o diretório está vazio
    },
    {
      key: 'claudemd',
      text: 'Run /init to create a CLAUDE.md file with instructions for Claude', // Executar /init para criar CLAUDE.md
      isComplete: hasClaudeMd,   // Completo se CLAUDE.md existe
      isCompletable: true,       // Pode ser completado
      isEnabled: !isWorkspaceDirEmpty, // Habilitado apenas se o diretório NÃO está vazio
    },
  ]
}

// Verifica se o onboarding do projeto foi concluído (todos os passos habilitados e completáveis foram feitos)
export function isProjectOnboardingComplete(): boolean {
  return getSteps()
    // Filtra apenas passos que são completáveis e estão habilitados
    .filter(({ isCompletable, isEnabled }) => isCompletable && isEnabled)
    // Verifica se todos os passos filtrados estão completos
    .every(({ isComplete }) => isComplete)
}

// Marca o onboarding do projeto como concluído se todas as condições forem atendidas
export function maybeMarkProjectOnboardingComplete(): void {
  // Atalho com configuração em cache — isProjectOnboardingComplete() acessa
  // o sistema de arquivos, e REPL.tsx chama isso a cada envio de prompt.
  if (getCurrentProjectConfig().hasCompletedProjectOnboarding) {
    return // Já está marcado como concluído, não faz nada
  }
  // Se o onboarding está completo, salva na configuração
  if (isProjectOnboardingComplete()) {
    saveCurrentProjectConfig(current => ({
      ...current,
      hasCompletedProjectOnboarding: true, // Marca como concluído
    }))
  }
}

// Função memoizada que determina se o onboarding do projeto deve ser exibido
export const shouldShowProjectOnboarding = memoize((): boolean => {
  // Obtém a configuração atual do projeto
  const projectConfig = getCurrentProjectConfig()
  // Atalho com configuração em cache antes de isProjectOnboardingComplete()
  // acessar o sistema de arquivos — isso roda durante a primeira renderização.
  if (
    projectConfig.hasCompletedProjectOnboarding ||    // Já concluiu o onboarding
    projectConfig.projectOnboardingSeenCount >= 4 ||  // Já viu o onboarding 4+ vezes
    process.env.IS_DEMO                               // Está em modo de demonstração
  ) {
    return false // Não mostrar o onboarding
  }

  // Mostra se o onboarding NÃO está completo
  return !isProjectOnboardingComplete()
})

// Incrementa o contador de vezes que o onboarding do projeto foi exibido
export function incrementProjectOnboardingSeenCount(): void {
  saveCurrentProjectConfig(current => ({
    ...current,
    projectOnboardingSeenCount: current.projectOnboardingSeenCount + 1, // Incrementa o contador
  }))
}
