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

  async function specialty(id: string) {
    try {
      setDoctors(await api(`/doctors?specialty_id=${id}`));
    } catch (e) {
      setError((e as Error).message);
    }
  }

  async function doctor(id: string) {
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

  return <div>
    <h2>Reservar cita</h2>
    <select onChange={e => specialty(e.target.value)}>
      <option>Especialidad</option>
      {specialties.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
    </select>
    <select onChange={e => doctor(e.target.value)}>
      <option>Médico</option>
      {doctors.map(d => <option key={d.id} value={d.id}>{d.full_name}</option>)}
    </select>
    {slots.map(s => <div key={s.id}>{s.starts_at}<button onClick={() => reserve(s.id)}>Reservar</button></div>)}
  </div>;
}
