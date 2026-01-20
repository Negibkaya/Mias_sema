import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { getProject, updateProject } from "../api/projects";
import Layout from "../components/Layout";
import RolesInput from "../components/RolesInput";

export default function ProjectEdit() {
  const { projectId } = useParams();
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    loadProject();
  }, [projectId]);

  const loadProject = async () => {
    try {
      const project = await getProject(projectId);
      setName(project.name);
      setDescription(project.description || "");
      setRoles(project.roles || []);
    } catch (err) {
      setError("Проект не найден");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim()) {
      setError("Введите название проекта");
      return;
    }

    setSaving(true);
    setError("");

    try {
      await updateProject(projectId, {
        name: name.trim(),
        description: description.trim() || null,
        roles: roles.length > 0 ? roles : null,
      });
      navigate(`/projects/${projectId}`);
    } catch (err) {
      setError(err.response?.data?.detail || "Ошибка при сохранении");
    } finally {
      setSaving(false);
    }
  };

  const totalPeople = roles.reduce((sum, r) => sum + r.count, 0);

  if (loading)
    return (
      <Layout>
        <div className="loading">Загрузка...</div>
      </Layout>
    );

  return (
    <Layout>
      <Link
        to={`/projects/${projectId}`}
        style={{ display: "inline-block", marginBottom: "16px" }}
      >
        ← Назад к проекту
      </Link>

      <h1>Редактирование проекта</h1>

      <div className="card">
        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Название проекта *</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>Описание</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
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
            <button type="submit" className="primary" disabled={saving}>
              {saving ? "Сохранение..." : "Сохранить"}
            </button>
            <Link to={`/projects/${projectId}`}>
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
