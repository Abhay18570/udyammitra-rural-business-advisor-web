import { useEffect, useState } from 'react'
import { isAxiosError } from 'axios'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/authContextValue'
import { getAdminData } from '../../services/adminService'

export type AdminDataState<T> = { status: 'loading' } | { status: 'ready'; data: T } | { status: 'error'; code?: number }
export function useAdminData<T>(path: string) {
  const [result, setResult] = useState<{ path: string; state: AdminDataState<T> }>({ path, state: { status: 'loading' } })
  const [revision, setRevision] = useState(0)
  const { logout } = useAuth()
  const navigate = useNavigate()
  useEffect(() => {
    const controller = new AbortController()
    getAdminData<T>(path, controller.signal).then(data => {
      if (!controller.signal.aborted) setResult({ path, state: { status: 'ready', data } })
    }).catch(error => {
      if (controller.signal.aborted) return
      const code = isAxiosError(error) ? error.response?.status : undefined
      if (code === 401) { logout(); navigate('/login', { replace: true }); return }
      setResult({ path, state: { status: 'error', code } })
    })
    return () => controller.abort()
  }, [path, revision, logout, navigate])
  return { state: result.path === path ? result.state : { status: 'loading' } as AdminDataState<T>, retry: () => { setResult({ path, state: { status: 'loading' } }); setRevision(value => value + 1) } }
}
