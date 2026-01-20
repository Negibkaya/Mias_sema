import { Link } from "react-router-dom";

export default function ProjectCard({ project }) {
  const totalPeople = project.roles?.reduce((sum, r) => sum + r.count, 0) || 0;

  return (
    <div className="card">
      <h3 style={{ marginBottom: "8px" }}>
        <Link to={`/projects/${project.id}`}>{project.name}</Link>
      </h3>

      {project.description && (
        <p style={{ color: "#666", marginBottom: "12px", fontSize: "14px" }}>
          {project.description.length > 150
            ? project.description.slice(0, 150) + "..."
            : project.description}
        </p>
      )}

      {project.roles?.length > 0 ? (
        <div>
          <span style={{ fontSize: "12px", color: "#888" }}>
            Команда ({totalPeople} чел.):
          </span>
          <div style={{ marginTop: "6px" }}>
            {project.roles.map((role, idx) => (
              <span key={idx} className="tag">
                {role.name} × {role.count}
              </span>
            ))}
          </div>
        </div>
      ) : (
        <span style={{ color: "#999", fontSize: "14px" }}>Роли не указаны</span>
      )}
    </div>
  );
}
