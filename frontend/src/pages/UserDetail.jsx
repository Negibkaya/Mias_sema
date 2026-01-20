import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { getUser } from "../api/users";
import Layout from "../components/Layout";

export default function UserDetail() {
  const { userId } = useParams();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadUser();
  }, [userId]);

  const loadUser = async () => {
    try {
      const data = await getUser(userId);
      setUser(data);
    } catch (err) {
      setError("Пользователь не найден");
    } finally {
      setLoading(false);
    }
  };

  const getLevelClass = (level) => {
    if (level >= 7) return "level-high";
    if (level >= 4) return "level-mid";
    return "level-low";
  };

  if (loading)
    return (
      <Layout>
        <div className="loading">Загрузка...</div>
      </Layout>
    );
  if (error)
    return (
      <Layout>
        <div className="error-message">{error}</div>
      </Layout>
    );

  return (
    <Layout>
      <Link
        to="/users"
        style={{ display: "inline-block", marginBottom: "16px" }}
      >
        ← Назад к списку
      </Link>

      <div className="card">
        <h1>{user.name || user.username || `User #${user.id}`}</h1>

        <div style={{ marginBottom: "20px", color: "#666" }}>
          {user.username && <p>@{user.username}</p>}
          <p>Telegram ID: {user.telegram_id}</p>
        </div>

        {user.bio && (
          <div style={{ marginBottom: "20px" }}>
            <h3>О себе</h3>
            <p style={{ whiteSpace: "pre-wrap" }}>{user.bio}</p>
          </div>
        )}

        <div>
          <h3>Навыки</h3>
          {user.skills?.length > 0 ? (
            <div>
              {user.skills.map((skill, idx) => (
                <span key={idx} className={`tag ${getLevelClass(skill.level)}`}>
                  {skill.name} — {skill.level}/10
                </span>
              ))}
            </div>
          ) : (
            <p style={{ color: "#999" }}>Навыки не указаны</p>
          )}
        </div>
      </div>
    </Layout>
  );
}
