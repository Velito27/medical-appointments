import { useEffect, useState } from "react";
import { api } from "../services/api";

type Props = {
  token: string;
  setError: (value: string) => void;
  setMessage: (value: string) => void;
};

type Appointment = {
  id: number;
  doctor_name: string;
  specialty_name: string;
  scheduled_start: string;
  scheduled_end: string;
  status: string;
  reason: string | null;
};

export default function Patient({ token, setError, setMessage }: Props) {
  const [specialties, setSpecialties] = useState<any[]>([]);
  const [doctors, setDoctors] = useState<any[]>([]);
  const [slots, setSlots] = useState<any[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [selectedDoctor, setSelectedDoctor] = useState("");

  useEffect(() => {
    api("/specialties").then(setSpecialties).catch(e => setError(e.message));
    loadAppointments();
  }, []);

  async function loadAppointments() {
    try {
      setAppointments(await api("/appointments/me", {}, token));
    } catch (e) {
      setError((e as Error).message);
    }
  }

  async function chooseSpecialty(id: string) {
    try {
      setSelectedDoctor("");
      setSlots([]);
      if (!id) {
        setDoctors([]);
        return;
      }
      setDoctors(await api(`/doctors?specialty_id=${id}`));
    } catch (e) {
      setError((e as Error).message);
    }
  }

  async function chooseDoctor(id: string) {
    try {
      setSelectedDoctor(id);
      if (!id) {
        setSlots([]);
        return;
      }
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
      await loadAppointments();

      if (selectedDoctor) {
        setSlots(await api(`/doctors/${selectedDoctor}/availability`));
      }
    } catch (e) {
      setError((e as Error).message);
    }
  }

  async function cancelAppointment(id: number) {
    try {
      await api(`/appointments/${id}/cancel`, { method: "POST" }, token);
      setMessage("Cita cancelada");
      await loadAppointments();

      if (selectedDoctor) {
        setSlots(await api(`/doctors/${selectedDoctor}/availability`));
      }
    } catch (e) {
      setError((e as Error).message);
    }
  }

  function statusText(status: string) {
    if (status === "scheduled") return "Programada";
    if (status === "cancelled") return "Cancelada";
    if (status === "completed") return "Completada";
    return status;
  }

  return <>
    <section>
      <h2>Reservar cita</h2>
      <p>Selecciona una especialidad y médico disponible. Cada médico puede tener como máximo 3 citas activas.</p>

      <select onChange={e => chooseSpecialty(e.target.value)}>
        <option value="">Especialidad</option>
        {specialties.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
      </select>

      <select value={selectedDoctor} onChange={e => chooseDoctor(e.target.value)}>
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

    <section>
      <h2>Mis citas</h2>
      {appointments.length === 0 && <p>Aún no tienes citas reservadas.</p>}

      {appointments.map(a => (
        <div className="card appointment-card" key={a.id}>
          <div>
            <strong>{a.doctor_name}</strong>
            <div>{a.specialty_name}</div>
            <div>{new Date(a.scheduled_start).toLocaleString()}</div>
            <div>Estado: {statusText(a.status)}</div>
          </div>

          {a.status === "scheduled" && (
            <button onClick={() => cancelAppointment(a.id)}>Cancelar cita</button>
          )}
        </div>
      ))}
    </section>
  </>;
}
