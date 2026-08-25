type Props = {
  setRole: (role: string) => void;
};

export default function Access({ setRole }: Props) {
  return (
    <div className="login-page">
      <section className="login-card">
        <h1>Medical Appointments</h1>
        <p>Selecciona tu tipo de usuario</p>

        <button onClick={() => setRole("patient")}>Paciente</button>
        <button onClick={() => setRole("doctor")}>Doctor</button>
        <button onClick={() => setRole("admin")}>Administrador</button>
      </section>
    </div>
  );
}
