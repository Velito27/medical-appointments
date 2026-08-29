import { FormEvent, useState } from "react";
import { api } from "../services/api";

type Props = {
  setRegistering: (value: boolean) => void;
  setRole: (role: string) => void;
};

export default function Register({ setRegistering, setRole }: Props) {
  const [error, setError] = useState("");

  async function register(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);

    try {
      await api("/auth/register", {
        method: "POST",
        body: JSON.stringify({
          email: data.get("email"),
          password: data.get("password")
        })
      });

      alert("Cuenta creada. Ahora inicia sesión.");
      setRole("patient");
      setRegistering(false);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <div className="login-page">
      <section className="login-card">
        <h1>Crear cuenta</h1>
        <p>Regístrate como paciente</p>

        {error && <p className="error">{error}</p>}

        <form onSubmit={register}>
          <input name="email" type="email" placeholder="Correo" required />
          <input name="password" type="password" placeholder="Contraseña" minLength={8} required />
          <button>Registrarme</button>
        </form>

        <button onClick={() => setRegistering(false)}>Volver</button>
      </section>
    </div>
  );
}
