import { useEffect, useState } from "react";
import { api } from "../services/api";

type Props = { token: string; setError: (value: string) => void };

export default function Admin({ token, setError }: Props) {
  const [users, setUsers] = useState<any[]>([]);

  useEffect(() => {
    api("/admin/users", {}, token).then(setUsers).catch(e => setError(e.message));
  }, []);

  return <div>
    <h2>Admin</h2>
    {users.map(u => <p key={u.id}>{u.email}</p>)}
  </div>;
}
