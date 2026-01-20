import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { updateMe } from "../api/users";
import Layout from "../components/Layout";
import SkillsInput from "../components/SkillsInput";

export default function Profile() {
  const { user, refreshUser } = useAuth();
  const [name, setName] = useState("");
  const [bio, setBio] = useState("");
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (user) {
      setName(user.name || "");
      setBio(user.bio || "");
      setSkills(user.skills || []);
    }
  }, [user]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");

    try {
      await updateMe({ name, bio, skills });
      await refreshUser();
      setSuccess("Профиль успешно обновлён!");
    } catch (err) {
      setError(err.response?.data?.detail || "Ошибка при сохранении");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <h1>Мой профиль</h1>

      <div className="card">
        <div
          style={{
            marginBottom: "20px",
            padding: "16px",
            background: "#f5f5f5",
            borderRadius: "8px",
          }}
        >
          <p>
            <strong>Telegram ID:</strong> {user?.telegram_id}
          </p>
          <p>
            <strong>Username:</strong> @{user?.username || "—"}
          </p>
        </div>

        {success && <div className="success-message">{success}</div>}
        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Имя</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Ваше имя"
            />
          </div>

          <div className="form-group">
            <label>О себе</label>
            <textarea
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              placeholder="Расскажите о себе, опыте, интересах..."
              rows={4}
            />
          </div>

          <div className="form-group">
            <label>Навыки (уровень от 0 до 10)</label>
            <SkillsInput skills={skills} onChange={setSkills} />
          </div>

          <button type="submit" className="primary" disabled={loading}>
            {loading ? "Сохранение..." : "Сохранить"}
          </button>
        </form>
      </div>
    </Layout>
  );
}
