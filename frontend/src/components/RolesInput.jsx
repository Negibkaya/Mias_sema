import { useState } from "react";
import SkillsInput from "./SkillsInput";

export default function RolesInput({ roles = [], onChange }) {
  const [showAddRole, setShowAddRole] = useState(false);
  const [newRoleName, setNewRoleName] = useState("");
  const [newRoleCount, setNewRoleCount] = useState(1);
  const [newRoleSkills, setNewRoleSkills] = useState([]);

  const addRole = () => {
    if (!newRoleName.trim()) return;

    const exists = roles.some(
      (r) => r.name.toLowerCase() === newRoleName.trim().toLowerCase(),
    );
    if (exists) {
      alert("Такая роль уже добавлена");
      return;
    }

    onChange([
      ...roles,
      {
        name: newRoleName.trim(),
        count: newRoleCount,
        skills: newRoleSkills,
      },
    ]);

    setNewRoleName("");
    setNewRoleCount(1);
    setNewRoleSkills([]);
    setShowAddRole(false);
  };

  const removeRole = (index) => {
    onChange(roles.filter((_, i) => i !== index));
  };

  const updateRoleCount = (index, count) => {
    const updated = [...roles];
    updated[index] = { ...updated[index], count: Math.max(1, count) };
    onChange(updated);
  };

  const updateRoleSkills = (index, skills) => {
    const updated = [...roles];
    updated[index] = { ...updated[index], skills };
    onChange(updated);
  };

  return (
    <div>
      {/* Список ролей */}
      {roles.map((role, index) => (
        <div
          key={index}
          style={{
            border: "1px solid #ddd",
            borderRadius: "8px",
            padding: "16px",
            marginBottom: "12px",
            background: "#fafafa",
          }}
        >
          <div className="flex-between" style={{ marginBottom: "12px" }}>
            <h4 style={{ margin: 0 }}>{role.name}</h4>
            <button
              type="button"
              onClick={() => removeRole(index)}
              className="danger"
              style={{ padding: "4px 10px", fontSize: "12px" }}
            >
              Удалить
            </button>
          </div>

          <div className="form-group">
            <label>Количество человек</label>
            <input
              type="number"
              min="1"
              max="100"
              value={role.count}
              onChange={(e) =>
                updateRoleCount(index, parseInt(e.target.value) || 1)
              }
              style={{ maxWidth: "100px" }}
            />
          </div>

          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>Требуемые навыки</label>
            <SkillsInput
              skills={role.skills || []}
              onChange={(skills) => updateRoleSkills(index, skills)}
            />
          </div>
        </div>
      ))}

      {roles.length === 0 && !showAddRole && (
        <p style={{ color: "#999", marginBottom: "12px" }}>
          Роли не добавлены. Добавьте роли для подбора команды.
        </p>
      )}

      {/* Форма добавления роли */}
      {showAddRole ? (
        <div
          style={{
            border: "2px dashed #0066cc",
            borderRadius: "8px",
            padding: "16px",
            marginBottom: "12px",
            background: "#f0f7ff",
          }}
        >
          <h4 style={{ marginTop: 0, marginBottom: "16px" }}>Новая роль</h4>

          <div className="form-group">
            <label>Название роли *</label>
            <input
              type="text"
              value={newRoleName}
              onChange={(e) => setNewRoleName(e.target.value)}
              placeholder="Например: Backend Developer"
            />
          </div>

          <div className="form-group">
            <label>Количество человек</label>
            <input
              type="number"
              min="1"
              max="100"
              value={newRoleCount}
              onChange={(e) => setNewRoleCount(parseInt(e.target.value) || 1)}
              style={{ maxWidth: "100px" }}
            />
          </div>

          <div className="form-group">
            <label>Требуемые навыки (минимальный уровень)</label>
            <SkillsInput skills={newRoleSkills} onChange={setNewRoleSkills} />
          </div>

          <div className="flex">
            <button type="button" onClick={addRole} className="primary">
              Добавить роль
            </button>
            <button
              type="button"
              onClick={() => {
                setShowAddRole(false);
                setNewRoleName("");
                setNewRoleCount(1);
                setNewRoleSkills([]);
              }}
              className="secondary"
            >
              Отмена
            </button>
          </div>
        </div>
      ) : (
        <button
          type="button"
          onClick={() => setShowAddRole(true)}
          className="secondary"
          style={{ width: "100%" }}
        >
          + Добавить роль
        </button>
      )}
    </div>
  );
}
