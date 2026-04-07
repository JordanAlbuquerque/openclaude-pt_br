// Importa o hook useEffect do React para executar efeitos colaterais
import { useEffect } from 'react'
// Importa as funções de formatação de custo e salvamento de custos da sessão
import { formatTotalCost, saveCurrentSessionCosts } from './cost-tracker.js'
// Importa a função que verifica se o usuário tem acesso ao console de faturamento
import { hasConsoleBillingAccess } from './utils/billing.js'
// Importa o tipo de métricas de FPS (frames por segundo)
import type { FpsMetrics } from './utils/fpsTracker.js'

// Hook customizado que exibe o resumo de custos ao sair do processo
export function useCostSummary(
  getFpsMetrics?: () => FpsMetrics | undefined, // Função opcional para obter métricas de FPS
): void {
  // Registra o efeito colateral ao montar o componente
  useEffect(() => {
    // Define a função que será executada ao sair do processo
    const f = () => {
      // Se o usuário tem acesso ao faturamento, imprime o custo total no stdout
      if (hasConsoleBillingAccess()) {
        process.stdout.write('\n' + formatTotalCost() + '\n')
      }

      // Salva os custos da sessão atual, incluindo métricas de FPS se disponíveis
      saveCurrentSessionCosts(getFpsMetrics?.())
    }
    // Registra o listener para o evento 'exit' do processo
    process.on('exit', f)
    // Função de limpeza: remove o listener ao desmontar o componente
    return () => {
      process.off('exit', f)
    }
  }, []) // Array de dependências vazio = executa apenas uma vez ao montar
}
