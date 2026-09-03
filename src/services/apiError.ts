import axios from 'axios'
export function getApiErrorMessage(error: unknown, fallback: string): string { if (axios.isAxiosError<{ detail?: string }>(error)) return error.response?.data?.detail ?? (error.code === 'ERR_NETWORK' ? 'Unable to reach the authentication service. Please confirm the backend is running.' : fallback); return fallback }
