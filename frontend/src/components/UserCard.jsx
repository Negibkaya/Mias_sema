import { Link } from "react-router-dom";

export default function UserCard({ user, actions }) {
  const getLevelClass = (level) => {
    if (level >= 7) return "level-high";
    if (level >= 4) return "level-mid";
    return "level-low";
  };

  return (
    <div className="card">
      <div className="flex-between mb-20">
        <div>
          <h3 style={{ marginBottom: "4px" }}>
            <Link to={`/users/${user.id}`}>
              {user.name || user.username || `User #${user.id}`}
            </Link>
          </h3>
          {user.username && (
            <span style={{ color: "#666", fontSize: "14px" }}>
              @{user.username}
            </span>
          )}
        </div>
        {actions && <div className="flex">{actions}</div>}
      </div>

      {user.bio && (
        <p style={{ color: "#666", marginBottom: "12px", fontSize: "14px" }}>
          {user.bio}
        </p>
      )}

      <div>
        {user.skills?.map((skill, idx) => (
          <span key={idx} className={`tag ${getLevelClass(skill.level)}`}>
            {skill.name} ({skill.level})
          </span>
        ))}
        {(!user.skills || user.skills.length === 0) && (
          <span style={{ color: "#999", fontSize: "14px" }}>
            Навыки не указаны
          </span>
        )}
      </div>
    </div>
  );
}
