// Importa o módulo de asserções estritas do Node.js para testes
import assert from 'node:assert/strict'
// Importa o módulo de testes nativo do Node.js
import test from 'node:test'

// Importa a função que estamos testando
import { getDistImportSpecifier } from './import-specifier.mjs'

// Teste: verifica se a função gera corretamente uma URL file:// para dist/cli.mjs
test('builds a file URL import specifier for dist/cli.mjs', () => {
  // Chama a função com um caminho Windows de exemplo
  const specifier = getDistImportSpecifier('C:\\repo\\bin')

  // Verifica se o resultado é a URL esperada com barras normais
  assert.equal(
    specifier,
    'file:///C:/repo/dist/cli.mjs',
  )
})
