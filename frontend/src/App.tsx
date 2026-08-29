import { useEffect, useState } from "react";
import { api } from "./services/api";
import Login from "./pages/Login";
import Access from "./pages/Access";
import Register from "./pages/Register";
import Patient from "./pages/Patient";
import Doctor from "./pages/Doctor";
import Admin from "./pages/Admin";

export default function App() {
  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [user, setUser] = useState<any>(null);
  const [role, setRole] = useState("");
  const [registering, setRegistering] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) return;

    api("/auth/me", {}, token)
      .then(setUser)
      .catch(() => {
        localStorage.removeItem("token");
        setToken("");
      });
  }, [token]);

  function logout() {
    localStorage.removeItem("token");
    setToken("");
    setUser(null);
    setRole("");
    setRegistering(false);
  }

  if (!user) {
    if (registering) {
      return <Register setRegistering={setRegistering} setRole={setRole} />;
    }

    if (!role) {
      return <Access setRole={setRole} setRegistering={setRegistering} />;
    }

    return <Login setToken={setToken} setUser={setUser} role={role} setRole={setRole} />;
  }

  return (
    <main className="container">
      <header className="header">
        <h1>MedicOS</h1>
        <div>
          <span>{user.email}</span>
          <button onClick={logout}>Salir</button>
        </div>
      </header>

      {error && <p className="error">{error}</p>}
      {message && <p className="success">{message}</p>}

      {user.role === "patient" && <Patient token={token} setError={setError} setMessage={setMessage} />}
      {user.role === "doctor" && <Doctor token={token} setError={setError} setMessage={setMessage} />}
      {user.role === "admin" && <Admin token={token} setError={setError} />}
    </main>
  );
}
