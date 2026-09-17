import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import './App.css'

function App() {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return <div className="loading-state">Cargando...</div>
  }

  return (
    <Routes>
      <Route
        path="/"
        element={isAuthenticated ? <DashboardPage /> : <Navigate to="/login" replace />}
      />
      <Route
        path="/login"
        element={!isAuthenticated ? <LoginPage /> : <Navigate to="/" replace />}
      />
      <Route path="*" element={<Navigate to={isAuthenticated ? '/' : '/login'} replace />} />
    </Routes>
  )
}

export default App
