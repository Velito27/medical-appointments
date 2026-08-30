import { FormEvent, useState } from "react";
import { api } from "../services/api";

type Props = {
  setRegistering: (value: boolean) => void;
  setRole: (role: string) => void;
};

export default function Register({ setRegistering, setRole }: Props) {
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);

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

          <div className="password-field">
            <input
              name="password"
              type={showPassword ? "text" : "password"}
              placeholder="Contraseña"
              minLength={8}
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

          <button>Registrarme</button>
        </form>

        <button onClick={() => setRegistering(false)}>Volver</button>
      </section>
    </div>
  );
}
