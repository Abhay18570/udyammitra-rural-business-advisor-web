import { useEffect, useState } from 'react'
export function useCatalogRequest<T>(key: string, load: (signal: AbortSignal) => Promise<T>) {
  const [attempt, setAttempt] = useState(0)
  const requestKey = `${key}:${attempt}`
  const [result, setResult] = useState<{ key: string; data?: T; error?: unknown }>()
  useEffect(() => {
    const controller = new AbortController()
    load(controller.signal).then(data => { if (!controller.signal.aborted) setResult({ key: requestKey, data }) })
      .catch((error: unknown) => { if (!controller.signal.aborted) setResult({ key: requestKey, error }) })
    return () => controller.abort()
  }, [requestKey, load])
  return { data: result?.key === requestKey ? result.data : undefined, error: result?.key === requestKey ? result.error : undefined,
    loading: result?.key !== requestKey, retry: () => setAttempt(v => v + 1) }
}
