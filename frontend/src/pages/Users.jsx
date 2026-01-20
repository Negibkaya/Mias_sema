import { useState, useEffect } from "react";
import { getUsers } from "../api/users";
import Layout from "../components/Layout";
import UserCard from "../components/UserCard";

export default function Users() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const data = await getUsers();
      setUsers(data);
    } catch (err) {
      setError("Ошибка загрузки пользователей");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <h1>Пользователи</h1>

      {loading && <div className="loading">Загрузка...</div>}
      {error && <div className="error-message">{error}</div>}

      <div className="grid grid-2">
        {users.map((user) => (
          <UserCard key={user.id} user={user} />
        ))}
      </div>

      {!loading && users.length === 0 && (
        <div className="card" style={{ textAlign: "center", color: "#666" }}>
          Пользователей пока нет
        </div>
      )}
    </Layout>
  );
}
