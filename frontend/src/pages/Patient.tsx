import { useEffect, useState } from "react";
import { api } from "../services/api";

type Props = {
  token: string;
  setError: (value: string) => void;
  setMessage: (value: string) => void;
};

export default function Patient({ token, setError, setMessage }: Props) {
  const [specialties, setSpecialties] = useState<any[]>([]);
  const [doctors, setDoctors] = useState<any[]>([]);
  const [slots, setSlots] = useState<any[]>([]);

  useEffect(() => {
    api("/specialties").then(setSpecialties).catch(e => setError(e.message));
  }, []);

  async function chooseSpecialty(id: string) {
    try {
      setDoctors(await api(`/doctors?specialty_id=${id}`));
      setSlots([]);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  async function chooseDoctor(id: string) {
    try {
      setSlots(await api(`/doctors/${id}/availability`));
    } catch (e) {
      setError((e as Error).message);
    }
  }

  async function reserve(id: number) {
    try {
      await api("/appointments", {
        method: "POST",
        body: JSON.stringify({ slot_id: id, reason: "Consulta" })
      }, token);
      setMessage("Cita reservada");
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return <>
    <section>
      <h2>Reservar cita</h2>
      <p>Selecciona una especialidad y médico disponible.</p>
      <select onChange={e => chooseSpecialty(e.target.value)}>
        <option value="">Especialidad</option>
        {specialties.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
      </select>
      <select onChange={e => chooseDoctor(e.target.value)}>
        <option value="">Médico</option>
        {doctors.map(d => <option key={d.id} value={d.id}>{d.full_name}</option>)}
      </select>
    </section>

    <section>
      <h2>Horarios disponibles</h2>
      {slots.length === 0 && <p>No hay horarios disponibles.</p>}
      {slots.map(s => (
        <div className="card" key={s.id}>
          <span>{new Date(s.starts_at).toLocaleString()}</span>
          <button onClick={() => reserve(s.id)}>Reservar</button>
        </div>
      ))}
    </section>
  </>;
}
