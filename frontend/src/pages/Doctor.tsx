import { useEffect, useState } from "react";
import { api } from "../services/api";

type Props = {
  token: string;
  setError: (value: string) => void;
  setMessage: (value: string) => void;
};

export default function Doctor({ token, setError, setMessage }: Props) {
  const [slots, setSlots] = useState<any[]>([]);

  async function load() {
    setSlots(await api("/doctor/slots", {}, token));
  }

  useEffect(() => {
    load().catch(e => setError(e.message));
  }, []);

  async function addSlot(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);

    try {
      await api("/doctor/slots", {
        method: "POST",
        body: JSON.stringify({
          starts_at: data.get("starts_at"),
          ends_at: data.get("ends_at")
        })
      }, token);
      setMessage("Horario creado");
      event.currentTarget.reset();
      load();
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return <>
    <section>
      <h2>Panel del médico</h2>
      <p>Gestiona tus horarios disponibles.</p>
      <form onSubmit={addSlot}>
        <input name="starts_at" type="datetime-local" required />
        <input name="ends_at" type="datetime-local" required />
        <button>Agregar horario</button>
      </form>
    </section>

    <section>
      <h2>Mis horarios</h2>
      {slots.map(s => (
        <div className="card" key={s.id}>
          {new Date(s.starts_at).toLocaleString()}
        </div>
      ))}
    </section>
  </>;
}
