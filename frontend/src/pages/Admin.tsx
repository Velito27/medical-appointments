import { useEffect, useState } from "react";
import { api } from "../services/api";

type Props = {
  token: string;
  setError: (value: string) => void;
};

type Stats = {
  total_users: number;
  patients: number;
  doctors: number;
  active_appointments: number;
  total_logins: number;
  logins_today: number;
};

type LoginLog = {
  id: number;
  user_id: number;
  email: string;
  role: string;
  logged_at: string;
};

export default function Admin({ token, setError }: Props) {
  const [users, setUsers] = useState<any[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [logs, setLogs] = useState<LoginLog[]>([]);

  useEffect(() => {
    Promise.all([
      api("/admin/users", {}, token),
      api("/admin/stats", {}, token),
      api("/admin/login-history", {}, token),
    ])
      .then(([usersData, statsData, logsData]) => {
        setUsers(usersData);
        setStats(statsData);
        setLogs(logsData);
      })
      .catch(e => setError(e.message));
  }, []);

  function roleLabel(role: string) {
    if (role === "patient") return "Paciente";
    if (role === "doctor") return "Doctor";
    if (role === "admin") return "Administrador";
    return role;
  }

  return <>
    <section>
      <div className="admin-kicker">ADMIN PANEL</div>
      <h2>Panel administrador</h2>
      <p>Resumen de actividad y accesos recientes al sistema.</p>

      {stats && (
        <div className="admin-stats">
          <div className="stat-card">
            <span>Usuarios</span>
            <strong>{stats.total_users}</strong>
          </div>
          <div className="stat-card">
            <span>Pacientes</span>
            <strong>{stats.patients}</strong>
          </div>
          <div className="stat-card">
            <span>Doctores</span>
            <strong>{stats.doctors}</strong>
          </div>
          <div className="stat-card">
            <span>Citas activas</span>
            <strong>{stats.active_appointments}</strong>
          </div>
          <div className="stat-card">
            <span>Logins totales</span>
            <strong>{stats.total_logins}</strong>
          </div>
          <div className="stat-card">
            <span>Logins hoy</span>
            <strong>{stats.logins_today}</strong>
          </div>
        </div>
      )}
    </section>

    <section>
      <h2>Historial de accesos</h2>
      <p>Últimos 50 inicios de sesión exitosos.</p>

      {logs.length === 0 ? (
        <p>Aún no hay accesos registrados.</p>
      ) : (
        <div className="log-table-wrap">
          <table className="admin-log-table">
            <thead>
              <tr>
                <th>Usuario</th>
                <th>Rol</th>
                <th>Fecha y hora</th>
              </tr>
            </thead>
            <tbody>
              {logs.map(log => (
                <tr key={log.id}>
                  <td>{log.email}</td>
                  <td>{roleLabel(log.role)}</td>
                  <td>{new Date(log.logged_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>

    <section>
      <h2>Usuarios registrados</h2>
      {users.map(user => (
        <div className="card" key={user.id}>
          <span>{user.email}</span>
          <span>{roleLabel(user.role)}</span>
        </div>
      ))}
    </section>
  </>;
}
