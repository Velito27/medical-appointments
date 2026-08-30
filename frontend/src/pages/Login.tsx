import { FormEvent, useState } from "react";
import { api } from "../services/api";

type Props = {
  setToken: (token: string) => void;
  setUser: (user: any) => void;
  role?: string;
  setRole?: (role: string) => void;
};

export default function Login({ setToken, setUser, role, setRole }: Props) {
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  async function login(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);

    try {
      const isAdmin = role === "admin";
      const result = await api(isAdmin ? "/auth/admin-login" : "/auth/login", {
        method: "POST",
        body: JSON.stringify(
          isAdmin
            ? {
                username: data.get("username"),
                password: data.get("password")
              }
            : {
                email: data.get("email"),
                password: data.get("password")
              }
        )
      });

      if (role && result.user?.role !== role) {
        throw new Error("Usuario incorrecto para este acceso");
      }

      localStorage.setItem("token", result.access_token);
      setToken(result.access_token);
      setUser(result.user);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  const isAdmin = role === "admin";

  return (
    <div className="login-page">
      <section className={isAdmin ? "login-card admin-login-card" : "login-card"}>
        {isAdmin && <div className="admin-kicker">ADMIN ACCESS</div>}

        <h1>{role === "patient" ? "Paciente" : role === "doctor" ? "Doctor" : "Administrador"}</h1>
        <p>Ingresa a tu cuenta</p>

        {error && <p className="error">{error}</p>}

        <form onSubmit={login}>
          {isAdmin ? (
            <input name="username" type="text" placeholder="Admin" autoComplete="username" required />
          ) : (
            <input name="email" type="email" placeholder="Correo" autoComplete="email" required />
          )}

          <div className="password-field">
            <input
              name="password"
              type={showPassword ? "text" : "password"}
              placeholder={isAdmin ? "Clave" : "Contraseña"}
              autoComplete="current-password"
              required
            />

            <button
              className="password-toggle"
              type="button"
              onClick={() => setShowPassword(value => !value)}
              aria-label={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
              title={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
            >
              {showPassword ? (
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M3 3l18 18M10.6 10.7a2 2 0 002.7 2.7M9.9 4.2A10.5 10.5 0 0112 4c5.5 0 9 5 9 5a16 16 0 01-3.1 3.5M6.2 6.2C4.2 7.5 3 9 3 9s3.5 5 9 5c1.1 0 2.1-.2 3-.5" />
                </svg>
              ) : (
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M2.5 12s3.5-6 9.5-6 9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6z" />
                  <circle cx="12" cy="12" r="2.5" />
                </svg>
              )}
            </button>
          </div>

          <button className={isAdmin ? "admin-submit" : ""}>Entrar</button>
        </form>

        {setRole && <button onClick={() => setRole("")}>Volver</button>}
      </section>
    </div>
  );
}
