import { useQuery } from '@apollo/client/react'
import { useAuth } from '../context/AuthContext'
import { DASHBOARD_RESUMEN_QUERY } from '../lib/apollo'

export default function DashboardPage() {
  const { logout } = useAuth()
  const { data, loading, error } = useQuery(DASHBOARD_RESUMEN_QUERY, {
    fetchPolicy: 'network-only',
  })

  const summary = data?.dashboardResumen || {
    totalEstudiantes: 0,
    totalDocentes: 0,
    totalProyectos: 0,
    totalMaterias: 0,
    promedioPpaEstudiantes: 0,
  }

  return (
    <div className="dashboard-shell">
      <header className="dashboard-topbar">
        <div>
          <span className="badge">Dashboard</span>
          <h1>Gestión Académica</h1>
        </div>
        <button type="button" className="logout-btn" onClick={logout}>
          Cerrar sesión
        </button>
      </header>

      {error && (
        <div className="error-box" style={{ marginBottom: '20px' }}>
          No se pudo cargar el resumen: {error.message}
        </div>
      )}

      <section className="dashboard-grid">
        <article className="stat-card">
          <span>Total estudiantes</span>
          <strong>{loading ? '...' : summary.totalEstudiantes}</strong>
        </article>
        <article className="stat-card">
          <span>Total docentes</span>
          <strong>{loading ? '...' : summary.totalDocentes}</strong>
        </article>
        <article className="stat-card">
          <span>Total proyectos</span>
          <strong>{loading ? '...' : summary.totalProyectos}</strong>
        </article>
        <article className="stat-card">
          <span>Total materias</span>
          <strong>{loading ? '...' : summary.totalMaterias}</strong>
        </article>
        <article className="stat-card wide-card">
          <span>Promedio PPA</span>
          <strong>{loading ? '...' : Number(summary.promedioPpaEstudiantes).toFixed(2)}</strong>
        </article>
      </section>
    </div>
  )
}
