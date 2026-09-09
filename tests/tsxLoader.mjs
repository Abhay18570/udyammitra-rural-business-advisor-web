import { registerHooks } from 'node:module'
import { readFileSync, existsSync } from 'node:fs'
import ts from 'typescript'
registerHooks({
  resolve(specifier, context, next) {
    if (specifier === '@vis.gl/react-google-maps') return { url: new URL('./googleMapsMock.mjs', import.meta.url).href, shortCircuit: true }
    if (specifier.startsWith('.') && context.parentURL?.includes('/src/')) {
      for (const ext of ['.ts', '.tsx']) {
        const url = new URL(specifier + ext, context.parentURL)
        if (existsSync(url)) return { url: url.href, shortCircuit: true }
      }
    }
    return next(specifier, context)
  },
  load(url, context, next) {
    if (/\.tsx?$/.test(url) && url.includes('/src/')) {
      const source = readFileSync(new URL(url), 'utf8').replace('import.meta.env.VITE_GOOGLE_MAPS_API_KEY', 'globalThis.mapTestKey').replace('import.meta.env.VITE_API_BASE_URL', 'undefined')
      return { format: 'module', source: ts.transpileModule(source, { compilerOptions: { jsx: ts.JsxEmit.ReactJSX, module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ESNext } }).outputText, shortCircuit: true }
    }
    return next(url, context)
  },
})
