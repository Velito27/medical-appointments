type Props = {
  setRole: (role: string) => void;
  setRegistering: (value: boolean) => void;
};

export default function Access({ setRole, setRegistering }: Props) {
  return (
    <div className="login-page">
      <section className="login-card">
        <h1>MedicOS</h1>
        <p>Selecciona tu tipo de usuario</p>

        <button onClick={() => setRole("patient")}>Paciente</button>
        <button onClick={() => setRole("doctor")}>Doctor</button>

        <button className="register-link" onClick={() => setRegistering(true)}>
          ¿No tienes una cuenta? ¡Regístrate!
        </button>

        <button className="admin-access-button" onClick={() => setRole("admin")}>
          Administrador
        </button>
      </section>
    </div>
  );
}
