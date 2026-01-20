import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { createProject } from "../api/projects";
import Layout from "../components/Layout";
import RolesInput from "../components/RolesInput";

export default function ProjectCreate() {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim()) {
      setError("Введите название проекта");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const project = await createProject({
        name: name.trim(),
        description: description.trim() || null,
        roles: roles.length > 0 ? roles : null,
      });
      navigate(`/projects/${project.id}`);
    } catch (err) {
      setError(err.response?.data?.detail || "Ошибка при создании проекта");
    } finally {
      setLoading(false);
    }
  };

  // Подсчёт общего количества человек
  const totalPeople = roles.reduce((sum, r) => sum + r.count, 0);

  return (
    <Layout>
      <Link
        to="/projects"
        style={{ display: "inline-block", marginBottom: "16px" }}
      >
        ← Назад к проектам
      </Link>

      <h1>Новый проект</h1>

      <div className="card">
        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Название проекта *</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Например: AI Startup"
              required
            />
          </div>

          <div className="form-group">
            <label>Описание</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Опишите проект, цели, задачи..."
              rows={5}
            />
          </div>

          <div className="form-group">
            <label>
              Роли в команде
              {totalPeople > 0 && (
                <span style={{ fontWeight: "normal", color: "#666" }}>
                  {" "}
                  (всего нужно: {totalPeople} чел.)
                </span>
              )}
            </label>
            <RolesInput roles={roles} onChange={setRoles} />
          </div>

          <div className="flex">
            <button type="submit" className="primary" disabled={loading}>
              {loading ? "Создание..." : "Создать проект"}
            </button>
            <Link to="/projects">
              <button type="button" className="secondary">
                Отмена
              </button>
            </Link>
          </div>
        </form>
      </div>
    </Layout>
  );
}
