import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { loginWithCredentials, TOKEN_KEY } from '../lib/apollo'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY) || '')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(false)
  }, [])

  const login = async (username, password) => {
    const authData = await loginWithCredentials(username, password)
    setToken(authData.token)
    return authData
  }

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY)
    setToken('')
  }

  const value = useMemo(
    () => ({
      token,
      isAuthenticated: Boolean(token),
      loading,
      login,
      logout,
    }),
    [token, loading],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)

  if (!context) {
    throw new Error('useAuth debe usarse dentro de AuthProvider')
  }

  return context
}
