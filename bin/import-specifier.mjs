// Importa join (juntar caminhos POSIX) e win32 (operações de caminho Windows) do módulo path
import { join, win32 } from 'path'
// Importa pathToFileURL para converter caminhos do sistema em URLs file://
import { pathToFileURL } from 'url'

// Função que gera o especificador de importação para o arquivo dist/cli.mjs
export function getDistImportSpecifier(baseDir) {
  // Verifica se o diretório base é um caminho Windows (ex: C:\repo\bin)
  if (/^[A-Za-z]:\\/.test(baseDir)) {
    // No Windows, usa win32.join para construir o caminho corretamente
    const distPath = win32.join(baseDir, '..', 'dist', 'cli.mjs')
    // Converte barras invertidas do Windows para barras normais e retorna como URL file://
    return `file:///${distPath.replace(/\\/g, '/')}`
  }

  // Em sistemas POSIX (macOS/Linux), usa join padrão
  const joinImpl = join
  const distPath = joinImpl(baseDir, '..', 'dist', 'cli.mjs')
  // Converte o caminho para URL file:// usando a função nativa do Node.js
  return pathToFileURL(distPath).href
}
