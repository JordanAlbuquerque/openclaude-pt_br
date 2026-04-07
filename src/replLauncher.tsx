// Importa o React para uso de JSX
import React from 'react';
// Importa o tipo StatsStore para métricas e estatísticas
import type { StatsStore } from './context/stats.js';
// Importa o tipo Root que representa a raiz do renderer Ink
import type { Root } from './ink.js';
// Importa o tipo Props do componente REPL (Read-Eval-Print Loop)
import type { Props as REPLProps } from './screens/REPL.js';
// Importa o tipo de estado da aplicação
import type { AppState } from './state/AppStateStore.js';
// Importa o tipo de métricas de FPS (frames por segundo)
import type { FpsMetrics } from './utils/fpsTracker.js';

// Tipo que define as propriedades do componente wrapper da aplicação
type AppWrapperProps = {
  getFpsMetrics: () => FpsMetrics | undefined; // Função para obter métricas de FPS
  stats?: StatsStore;                          // Store de estatísticas (opcional)
  initialState: AppState;                      // Estado inicial da aplicação
};

// Função assíncrona que inicializa e renderiza o REPL (loop de leitura-avaliação-impressão)
export async function launchRepl(
  root: Root,                                                                    // Raiz do renderer Ink onde a UI será montada
  appProps: AppWrapperProps,                                                      // Props do componente App wrapper
  replProps: REPLProps,                                                           // Props do componente REPL
  renderAndRun: (root: Root, element: React.ReactNode) => Promise<void>          // Função que renderiza o elemento e executa o loop
): Promise<void> {
  // Importação dinâmica do componente App (lazy loading para melhor performance)
  const {
    App
  } = await import('./components/App.js');
  // Importação dinâmica do componente REPL (lazy loading para melhor performance)
  const {
    REPL
  } = await import('./screens/REPL.js');
  // Renderiza a árvore de componentes: App envolve o REPL com as props correspondentes
  await renderAndRun(root, <App {...appProps}>
      <REPL {...replProps} />
    </App>);
}
