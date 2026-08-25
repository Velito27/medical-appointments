import { useEffect, useState } from "react";
import { api } from "../services/api";

type Props = {
  token: string;
  setError: (value: string) => void;
};

export default function Admin({ token, setError }: Props) {
  const [users, setUsers] = useState<any[]>([]);

  useEffect(() => {
    api("/admin/users", {}, token)
      .then(setUsers)
      .catch(e => setError(e.message));
  }, []);

  return <>
    <section>
      <h2>Panel administrador</h2>
      <p>Gestiona los usuarios del sistema.</p>
    </section>

    <section>
      <h2>Usuarios registrados</h2>
      {users.map(user => (
        <div className="card" key={user.id}>
          <span>{user.email}</span>
          <span>{user.role}</span>
        </div>
      ))}
    </section>
  </>;
}
