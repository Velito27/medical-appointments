import { useEffect, useState } from "react";
import { api } from "../services/api";

type Props = { token: string; setError: (value: string) => void };

export default function Doctor({ token, setError }: Props) {
  const [slots, setSlots] = useState<any[]>([]);

  useEffect(() => {
    api("/doctor/slots", {}, token).then(setSlots).catch(e => setError(e.message));
  }, []);

  return <div>
    <h2>Doctor</h2>
    {slots.map(s => <p key={s.id}>{s.starts_at}</p>)}
  </div>;
}
