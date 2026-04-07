// Importa createElement e o tipo ReactNode do React para criar elementos e tipar nós
import { createElement, type ReactNode } from 'react'
// Importa o componente ThemeProvider do design system para prover o tema à aplicação
import { ThemeProvider } from './components/design-system/ThemeProvider.js'
// Importa a função de renderização do Ink e tipos relacionados
import inkRender, {
  type Instance,                           // Tipo da instância de renderização
  createRoot as inkCreateRoot,             // Função para criar a raiz de renderização
  type RenderOptions,                      // Tipo das opções de renderização
  type Root,                               // Tipo da raiz de renderização
} from './ink/root.js'

// Re-exporta os tipos para uso em outros módulos
export type { RenderOptions, Instance, Root }

// Envolve todas as chamadas de renderização do CC com ThemeProvider para que
// ThemedBox/ThemedText funcionem sem que cada local de chamada precise montá-lo.
// O Ink em si é agnóstico a temas.
function withTheme(node: ReactNode): ReactNode {
  // Cria um elemento ThemeProvider envolvendo o nó filho recebido
  return createElement(ThemeProvider, null, node)
}

// Função assíncrona para renderizar um nó React com tema aplicado
export async function render(
  node: ReactNode,                                    // Nó React a ser renderizado
  options?: NodeJS.WriteStream | RenderOptions,       // Opções de renderização ou stream de saída
): Promise<Instance> {
  // Renderiza o nó envolvido com o tema usando o renderer do Ink
  return inkRender(withTheme(node), options)
}

// Função assíncrona para criar uma raiz de renderização com tema
export async function createRoot(options?: RenderOptions): Promise<Root> {
  // Cria a raiz do Ink com as opções fornecidas
  const root = await inkCreateRoot(options)
  // Retorna a raiz com o método render sobrescrito para incluir o tema automaticamente
  return {
    ...root,
    render: node => root.render(withTheme(node)), // Aplica o tema a cada renderização
  }
}

// Re-exportações de componentes e utilitários do design system e do Ink
// Essas exportações tornam este arquivo o ponto de entrada central para todos os componentes de UI

export { color } from './components/design-system/color.js'                          // Utilitário de cores do design system
export type { Props as BoxProps } from './components/design-system/ThemedBox.js'      // Tipo de props do Box com tema
export { default as Box } from './components/design-system/ThemedBox.js'              // Componente Box com tema
export type { Props as TextProps } from './components/design-system/ThemedText.js'    // Tipo de props do Text com tema
export { default as Text } from './components/design-system/ThemedText.js'            // Componente Text com tema
export {
  ThemeProvider,       // Componente provedor de tema
  usePreviewTheme,     // Hook para pré-visualizar temas
  useTheme,            // Hook para acessar o tema atual
  useThemeSetting,     // Hook para acessar configurações de tema
} from './components/design-system/ThemeProvider.js'
export { Ansi } from './ink/Ansi.js'                                                  // Componente para renderizar texto ANSI
export type { Props as AppProps } from './ink/components/AppContext.js'                // Tipo de props do contexto do App
export type { Props as BaseBoxProps } from './ink/components/Box.js'                   // Tipo de props do Box base
export { default as BaseBox } from './ink/components/Box.js'                           // Componente Box base (sem tema)
export type {
  ButtonState,                                                                        // Tipo de estado do botão
  Props as ButtonProps,                                                               // Tipo de props do botão
} from './ink/components/Button.js'
export { default as Button } from './ink/components/Button.js'                        // Componente Button
export type { Props as LinkProps } from './ink/components/Link.js'                     // Tipo de props do Link
export { default as Link } from './ink/components/Link.js'                            // Componente Link
export type { Props as NewlineProps } from './ink/components/Newline.js'               // Tipo de props do Newline
export { default as Newline } from './ink/components/Newline.js'                      // Componente Newline (quebra de linha)
export { NoSelect } from './ink/components/NoSelect.js'                               // Componente que impede seleção
export { RawAnsi } from './ink/components/RawAnsi.js'                                 // Componente para ANSI raw (sem processamento)
export { default as Spacer } from './ink/components/Spacer.js'                        // Componente Spacer (espaçamento)
export type { Props as StdinProps } from './ink/components/StdinContext.js'            // Tipo de props do contexto stdin
export type { Props as BaseTextProps } from './ink/components/Text.js'                 // Tipo de props do Text base
export { default as BaseText } from './ink/components/Text.js'                        // Componente Text base (sem tema)
export type { DOMElement } from './ink/dom.js'                                        // Tipo de elemento DOM do Ink
export { ClickEvent } from './ink/events/click-event.js'                              // Evento de clique
export { EventEmitter } from './ink/events/emitter.js'                                // Emissor de eventos
export { Event } from './ink/events/event.js'                                         // Classe base de evento
export type { Key } from './ink/events/input-event.js'                                // Tipo de tecla pressionada
export { InputEvent } from './ink/events/input-event.js'                              // Evento de entrada (teclado)
export type { TerminalFocusEventType } from './ink/events/terminal-focus-event.js'     // Tipo de evento de foco do terminal
export { TerminalFocusEvent } from './ink/events/terminal-focus-event.js'             // Evento de foco/desfoco do terminal
export { FocusManager } from './ink/focus.js'                                         // Gerenciador de foco de elementos
export type { FlickerReason } from './ink/frame.js'                                   // Tipo de razão de flicker (cintilação)
export { useAnimationFrame } from './ink/hooks/use-animation-frame.js'                // Hook para animação por frame
export { default as useApp } from './ink/hooks/use-app.js'                            // Hook para acessar o contexto do App
export { default as useInput } from './ink/hooks/use-input.js'                        // Hook para capturar entrada do teclado
export { useAnimationTimer, useInterval } from './ink/hooks/use-interval.js'          // Hooks para timers e intervalos
export { useSelection } from './ink/hooks/use-selection.js'                           // Hook para gerenciar seleção
export { default as useStdin } from './ink/hooks/use-stdin.js'                        // Hook para acessar stdin
export { useTabStatus } from './ink/hooks/use-tab-status.js'                          // Hook para status da aba do terminal
export { useTerminalFocus } from './ink/hooks/use-terminal-focus.js'                  // Hook para foco do terminal
export { useTerminalTitle } from './ink/hooks/use-terminal-title.js'                  // Hook para definir título do terminal
export { useTerminalViewport } from './ink/hooks/use-terminal-viewport.js'            // Hook para dimensões do viewport do terminal
export { default as measureElement } from './ink/measure-element.js'                  // Função para medir dimensões de elementos
export { supportsTabStatus } from './ink/termio/osc.js'                               // Verifica suporte a status de aba OSC
export { default as wrapText } from './ink/wrap-text.js'                              // Função para quebrar texto em linhas
