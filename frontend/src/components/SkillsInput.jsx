import { useState } from "react";

export default function SkillsInput({ skills = [], onChange }) {
  const [newSkillName, setNewSkillName] = useState("");
  const [newSkillLevel, setNewSkillLevel] = useState(5);

  const addSkill = () => {
    if (!newSkillName.trim()) return;

    const exists = skills.some(
      (s) => s.name.toLowerCase() === newSkillName.trim().toLowerCase(),
    );
    if (exists) {
      alert("Такой навык уже добавлен");
      return;
    }

    onChange([...skills, { name: newSkillName.trim(), level: newSkillLevel }]);
    setNewSkillName("");
    setNewSkillLevel(5);
  };

  const removeSkill = (index) => {
    onChange(skills.filter((_, i) => i !== index));
  };

  const getLevelClass = (level) => {
    if (level >= 7) return "level-high";
    if (level >= 4) return "level-mid";
    return "level-low";
  };

  return (
    <div>
      <div style={{ marginBottom: "12px" }}>
        {skills.map((skill, index) => (
          <span
            key={index}
            className={`tag ${getLevelClass(skill.level)}`}
            style={{ marginRight: "8px" }}
          >
            {skill.name} ({skill.level}/10)
            <button
              type="button"
              onClick={() => removeSkill(index)}
              style={{
                background: "none",
                border: "none",
                marginLeft: "6px",
                padding: "0",
                cursor: "pointer",
                color: "inherit",
              }}
            >
              ×
            </button>
          </span>
        ))}
        {skills.length === 0 && (
          <span style={{ color: "#999" }}>Навыки не добавлены</span>
        )}
      </div>

      <div className="flex" style={{ gap: "8px" }}>
        <input
          type="text"
          placeholder="Название навыка"
          value={newSkillName}
          onChange={(e) => setNewSkillName(e.target.value)}
          style={{ flex: 2 }}
          onKeyDown={(e) =>
            e.key === "Enter" && (e.preventDefault(), addSkill())
          }
        />
        <input
          type="number"
          min="0"
          max="10"
          value={newSkillLevel}
          onChange={(e) => setNewSkillLevel(Number(e.target.value))}
          style={{ flex: 1, maxWidth: "80px" }}
        />
        <button type="button" onClick={addSkill} className="secondary">
          Добавить
        </button>
      </div>
    </div>
  );
}
