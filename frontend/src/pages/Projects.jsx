import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { getProjects } from "../api/projects";
import Layout from "../components/Layout";
import ProjectCard from "../components/ProjectCard";

export default function Projects() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const data = await getProjects();
      setProjects(data);
    } catch (err) {
      setError("Ошибка загрузки проектов");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="flex-between mb-20">
        <h1 style={{ marginBottom: 0 }}>Проекты</h1>
        <Link to="/projects/new">
          <button className="primary">+ Создать проект</button>
        </Link>
      </div>

      {loading && <div className="loading">Загрузка...</div>}
      {error && <div className="error-message">{error}</div>}

      <div className="grid grid-2">
        {projects.map((project) => (
          <ProjectCard key={project.id} project={project} />
        ))}
      </div>

      {!loading && projects.length === 0 && (
        <div className="card" style={{ textAlign: "center", color: "#666" }}>
          Проектов пока нет. <Link to="/projects/new">Создайте первый!</Link>
        </div>
      )}
    </Layout>
  );
}
