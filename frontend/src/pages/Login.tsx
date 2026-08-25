import { FormEvent, useState } from "react";
import { api } from "../services/api";

type Props = {
  setToken: (token: string) => void;
  setUser: (user: any) => void;
};

export default function Login({ setToken, setUser }: Props) {
  const [error, setError] = useState("");

  async function login(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);

    try {
      const result = await api("/auth/login", {
        method: "POST",
        body: JSON.stringify({
          email: data.get("email"),
          password: data.get("password")
        })
      });

      localStorage.setItem("token", result.access_token);
      setToken(result.access_token);
      setUser(result.user);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <div className="login-page">
      <section className="login-card">
        <h1>🏥 Medical Appointments</h1>
        <p>Ingresa a tu cuenta</p>

        {error && <p className="error">{error}</p>}

        <form onSubmit={login}>
          <input name="email" type="email" placeholder="Correo" required />
          <input name="password" type="password" placeholder="Contraseña" required />
          <button>Entrar</button>
        </form>
      </section>
    </div>
  );
}
