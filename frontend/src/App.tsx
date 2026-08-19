import { FormEvent, useEffect, useState } from "react";

type User = { id: number; email: string; role: string; is_active: boolean };
type Specialty = { id: number; name: string; description: string | null; is_active: boolean };
type Doctor = { id: number; email: string; full_name: string; specialty_id: number; specialty_name: string; is_active: boolean };
type Slot = { id: number; doctor_id: number; starts_at: string; ends_at: string; is_active: boolean; is_booked: boolean };
type Appointment = { id: number; patient_email: string; doctor_name: string; specialty_name: string; scheduled_start: string; status: string };

const API = "/api";

async function api(path: string, options: RequestInit = {}, token = "") {
  const headers = new Headers(options.headers);
  if (options.body) headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const response = await fetch(`${API}${path}`, { ...options, headers });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(typeof data.detail === "string" ? data.detail : `Error ${response.status}`);
  }
  if (response.status === 204) return null;
  return response.json();
}

export default function App() {
  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!token) return;
    api("/auth/me", {}, token)
      .then(setUser)
      .catch(() => { localStorage.removeItem("token"); setToken(""); setUser(null); });
  }, [token]);

  async function login(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    setError("");
    try {
      const result = await api("/auth/login", { method: "POST", body: JSON.stringify({ email: data.get("email"), password: data.get("password") }) });
      localStorage.setItem("token", result.access_token);
      setToken(result.access_token);
      setUser(result.user);
    } catch (e) { setError((e as Error).message); }
  }

  async function register(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    setError("");
    try {
      await api("/auth/register", { method: "POST", body: JSON.stringify({ email: data.get("email"), password: data.get("password") }) });
      form.reset();
      setMessage("Usuario registrado. Ahora inicia sesión.");
    } catch (e) { setError((e as Error).message); }
  }

  function logout() {
    localStorage.removeItem("token");
    setToken("");
    setUser(null);
  }

  if (!user) return <div className="container">
    <h1>Sistema de citas médicas</h1>
    {error && <p className="error">{error}</p>}
    {message && <p className="success">{message}</p>}
    <section><h2>Login</h2><form onSubmit={login}><input name="email" type="email" placeholder="Correo" required /><input name="password" type="password" placeholder="Contraseña" required /><button>Entrar</button></form></section>
    <section><h2>Registro de paciente</h2><form onSubmit={register}><input name="email" type="email" placeholder="Correo" required /><input name="password" type="password" minLength={8} placeholder="Contraseña" required /><button>Registrarme</button></form></section>
  </div>;

  return <div className="container">
    <h1>Sistema de citas médicas</h1>
    <p>{user.email} — <b>{user.role}</b> <button onClick={logout}>Salir</button></p>
    {error && <p className="error">{error}</p>}
    {message && <p className="success">{message}</p>}
    {user.role === "patient" && <Patient token={token} setError={setError} setMessage={setMessage} />}
    {user.role === "doctor" && <DoctorPanel token={token} setError={setError} setMessage={setMessage} />}
    {user.role === "admin" && <AdminPanel token={token} setError={setError} setMessage={setMessage} />}
  </div>;
}

function Patient({ token, setError, setMessage }: { token: string; setError: (x: string) => void; setMessage: (x: string) => void }) {
  const [specialties, setSpecialties] = useState<Specialty[]>([]);
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [slots, setSlots] = useState<Slot[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);

  async function loadAppointments() { setAppointments(await api("/appointments/me", {}, token)); }
  useEffect(() => { api("/specialties").then(setSpecialties).catch(e => setError(e.message)); loadAppointments().catch(e => setError(e.message)); }, []);

  async function chooseSpecialty(id: string) {
    setDoctors(id ? await api(`/doctors?specialty_id=${id}`) : []);
    setSlots([]);
  }
  async function chooseDoctor(id: string) { setSlots(id ? await api(`/doctors/${id}/availability`) : []); }
  async function book(slotId: number) {
    try { await api("/appointments", { method: "POST", body: JSON.stringify({ slot_id: slotId, reason: "Consulta médica" }) }, token); setMessage("Cita reservada"); setSlots(slots.filter(s => s.id !== slotId)); await loadAppointments(); } catch (e) { setError((e as Error).message); }
  }
  async function cancel(id: number) {
    try { await api(`/appointments/${id}/cancel`, { method: "POST" }, token); setMessage("Cita cancelada"); await loadAppointments(); } catch (e) { setError((e as Error).message); }
  }

  return <>
    <section><h2>Reservar cita</h2>
      <select onChange={e => chooseSpecialty(e.target.value)}><option value="">Especialidad</option>{specialties.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}</select>
      <select onChange={e => chooseDoctor(e.target.value)}><option value="">Médico</option>{doctors.map(d => <option key={d.id} value={d.id}>{d.full_name}</option>)}</select>
      <ul>{slots.map(s => <li key={s.id}>{new Date(s.starts_at).toLocaleString()} <button onClick={() => book(s.id)}>Reservar</button></li>)}</ul>
    </section>
    <section><h2>Mis citas</h2><table><tbody>{appointments.map(a => <tr key={a.id}><td>{a.doctor_name}</td><td>{a.specialty_name}</td><td>{new Date(a.scheduled_start).toLocaleString()}</td><td>{a.status}</td><td>{a.status === "scheduled" && <button onClick={() => cancel(a.id)}>Cancelar</button>}</td></tr>)}</tbody></table></section>
  </>;
}

function DoctorPanel({ token, setError, setMessage }: { token: string; setError: (x: string) => void; setMessage: (x: string) => void }) {
  const [slots, setSlots] = useState<Slot[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  async function load() { setSlots(await api("/doctor/slots", {}, token)); setAppointments(await api("/doctor/appointments", {}, token)); }
  useEffect(() => { load().catch(e => setError(e.message)); }, []);
  async function addSlot(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); const form = event.currentTarget; const data = new FormData(form);
    try { await api("/doctor/slots", { method: "POST", body: JSON.stringify({ starts_at: data.get("starts_at"), ends_at: data.get("ends_at") }) }, token); form.reset(); setMessage("Horario creado"); await load(); } catch (e) { setError((e as Error).message); }
  }
  async function updateAppointment(id: number, status: string) {
    try { await api(`/doctor/appointments/${id}`, { method: "PATCH", body: JSON.stringify({ status }) }, token); await load(); } catch (e) { setError((e as Error).message); }
  }
  return <>
    <section><h2>Mis horarios</h2><form onSubmit={addSlot}><input name="starts_at" type="datetime-local" required /><input name="ends_at" type="datetime-local" required /><button>Agregar</button></form><ul>{slots.map(s => <li key={s.id}>{new Date(s.starts_at).toLocaleString()} - {s.is_booked ? "reservado" : "libre"}</li>)}</ul></section>
    <section><h2>Mis citas</h2><table><tbody>{appointments.map(a => <tr key={a.id}><td>{a.patient_email}</td><td>{new Date(a.scheduled_start).toLocaleString()}</td><td>{a.status}</td><td>{a.status === "scheduled" && <><button onClick={() => updateAppointment(a.id, "completed")}>Completar</button><button onClick={() => updateAppointment(a.id, "cancelled")}>Cancelar</button></>}</td></tr>)}</tbody></table></section>
  </>;
}

function AdminPanel({ token, setError, setMessage }: { token: string; setError: (x: string) => void; setMessage: (x: string) => void }) {
  const [users, setUsers] = useState<User[]>([]);
  const [specialties, setSpecialties] = useState<Specialty[]>([]);
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  async function load() { setUsers(await api("/admin/users", {}, token)); setSpecialties(await api("/specialties")); setDoctors(await api("/admin/doctors", {}, token)); }
  useEffect(() => { load().catch(e => setError(e.message)); }, []);
  async function addSpecialty(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); const form = event.currentTarget; const data = new FormData(form);
    try { await api("/admin/specialties", { method: "POST", body: JSON.stringify({ name: data.get("name"), description: data.get("description") || null }) }, token); form.reset(); setMessage("Especialidad creada"); await load(); } catch (e) { setError((e as Error).message); }
  }
  async function addDoctor(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); const form = event.currentTarget; const data = new FormData(form);
    try { await api("/admin/doctors", { method: "POST", body: JSON.stringify({ email: data.get("email"), password: data.get("password"), full_name: data.get("full_name"), specialty_id: Number(data.get("specialty_id")) }) }, token); form.reset(); setMessage("Médico creado"); await load(); } catch (e) { setError((e as Error).message); }
  }
  async function toggleUser(user: User) {
    try { await api(`/admin/users/${user.id}/active`, { method: "PATCH", body: JSON.stringify({ is_active: !user.is_active }) }, token); await load(); } catch (e) { setError((e as Error).message); }
  }
  return <>
    <section><h2>Especialidades</h2><form onSubmit={addSpecialty}><input name="name" placeholder="Nombre" required /><input name="description" placeholder="Descripción" /><button>Crear</button></form><ul>{specialties.map(s => <li key={s.id}>{s.name}</li>)}</ul></section>
    <section><h2>Médicos</h2><form onSubmit={addDoctor}><input name="email" type="email" placeholder="Correo" required /><input name="password" type="password" minLength={8} placeholder="Contraseña" required /><input name="full_name" placeholder="Nombre" required /><select name="specialty_id" required><option value="">Especialidad</option>{specialties.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}</select><button>Crear médico</button></form><ul>{doctors.map(d => <li key={d.id}>{d.full_name} - {d.specialty_name}</li>)}</ul></section>
    <section><h2>Usuarios</h2><table><tbody>{users.map(u => <tr key={u.id}><td>{u.email}</td><td>{u.role}</td><td>{u.is_active ? "activo" : "inactivo"}</td><td><button onClick={() => toggleUser(u)}>{u.is_active ? "Desactivar" : "Activar"}</button></td></tr>)}</tbody></table></section>
  </>;
}
