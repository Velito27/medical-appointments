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

          <input
            name="password"
            type="password"
            placeholder={isAdmin ? "Clave" : "Contraseña"}
            autoComplete="current-password"
            required
          />

          <button className={isAdmin ? "admin-submit" : ""}>Entrar</button>
        </form>

        {setRole && <button onClick={() => setRole("")}>Volver</button>}
      </section>
    </div>
  );
}
