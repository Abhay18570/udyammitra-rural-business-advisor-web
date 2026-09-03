const TOKEN_KEY = 'udyammitra_access_token'

export const tokenStorage = {
  get(): string | null { return localStorage.getItem(TOKEN_KEY) ?? sessionStorage.getItem(TOKEN_KEY) },
  set(token: string, persistent = false): void { this.clear(); (persistent ? localStorage : sessionStorage).setItem(TOKEN_KEY, token) },
  clear(): void { localStorage.removeItem(TOKEN_KEY); sessionStorage.removeItem(TOKEN_KEY) },
}
