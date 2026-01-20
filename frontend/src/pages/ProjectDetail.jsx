import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  getProject,
  deleteProject,
  getProjectMembers,
  addProjectMember,
  removeProjectMember,
} from "../api/projects";
import { getUsers } from "../api/users";
import { matchCandidates } from "../api/ai";
import Layout from "../components/Layout";
import UserCard from "../components/UserCard";

export default function ProjectDetail() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [project, setProject] = useState(null);
  const [members, setMembers] = useState([]);
  const [allUsers, setAllUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // AI Matching
  const [matching, setMatching] = useState(false);
  const [matchResults, setMatchResults] = useState(null);

  // Add member
  const [showAddMember, setShowAddMember] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState("");
  const [selectedRoleName, setSelectedRoleName] = useState("");

  useEffect(() => {
    loadData();
  }, [projectId]);

  const loadData = async () => {
    try {
      const [proj, memb, users] = await Promise.all([
        getProject(projectId),
        getProjectMembers(projectId),
        getUsers(),
      ]);
      setProject(proj);
      setMembers(memb);
      setAllUsers(users);
    } catch (err) {
      setError("Проект не найден");
    } finally {
      setLoading(false);
    }
  };

  const isOwner = project && user && project.owner_id === user.id;

  const handleDelete = async () => {
    if (!confirm("Удалить проект? Это действие нельзя отменить.")) return;
    try {
      await deleteProject(projectId);
      navigate("/projects");
    } catch (err) {
      alert(err.response?.data?.detail || "Ошибка удаления");
    }
  };

  const handleAddMember = async () => {
    if (!selectedUserId) return;
    try {
      await addProjectMember(
        projectId,
        selectedUserId,
        selectedRoleName || null,
      );
      await loadData();
      setShowAddMember(false);
      setSelectedUserId("");
      setSelectedRoleName("");
    } catch (err) {
      alert(err.response?.data?.detail || "Ошибка добавления");
    }
  };

  const handleRemoveMember = async (userId) => {
    if (!confirm("Удалить участника из проекта?")) return;
    try {
      await removeProjectMember(projectId, userId);
      await loadData();
    } catch (err) {
      alert(err.response?.data?.detail || "Ошибка удаления");
    }
  };

  const handleMatch = async () => {
    setMatching(true);
    setMatchResults(null);
    try {
      const results = await matchCandidates(projectId, null, 3);
      setMatchResults(results);
    } catch (err) {
      alert(err.response?.data?.detail || "Ошибка AI сервиса");
    } finally {
      setMatching(false);
    }
  };

  const handleAddFromMatch = async (candidateId, roleName) => {
    try {
      await addProjectMember(projectId, candidateId, roleName);
      await loadData();
      // Обновляем результаты матчинга
      if (matchResults) {
        setMatchResults((prev) =>
          prev.map((role) => ({
            ...role,
            filled: role.role_name === roleName ? role.filled + 1 : role.filled,
            candidates: role.candidates.filter((c) => c.id !== candidateId),
          })),
        );
      }
    } catch (err) {
      alert(err.response?.data?.detail || "Ошибка добавления");
    }
  };

  const memberIds = members.map((m) => m.id);
  const availableUsers = allUsers.filter(
    (u) => u.id !== project?.owner_id && !memberIds.includes(u.id),
  );

  // Группировка участников по ролям
  const membersByRole = {};
  members.forEach((m) => {
    const role = m.role_name || "Без роли";
    if (!membersByRole[role]) membersByRole[role] = [];
    membersByRole[role].push(m);
  });

  // Подсчёт нужного количества
  const totalNeeded = project?.roles?.reduce((sum, r) => sum + r.count, 0) || 0;
  const totalFilled = members.length;

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
        to="/projects"
        style={{ display: "inline-block", marginBottom: "16px" }}
      >
        ← Назад к проектам
      </Link>

      <div className="card">
        <div className="flex-between mb-20">
          <h1 style={{ marginBottom: 0 }}>{project.name}</h1>
          {isOwner && (
            <div className="flex">
              <Link to={`/projects/${projectId}/edit`}>
                <button className="secondary">Редактировать</button>
              </Link>
              <button className="danger" onClick={handleDelete}>
                Удалить
              </button>
            </div>
          )}
        </div>

        {project.description && (
          <p style={{ marginBottom: "20px", whiteSpace: "pre-wrap" }}>
            {project.description}
          </p>
        )}

        {/* Роли проекта */}
        {project.roles && project.roles.length > 0 && (
          <div style={{ marginBottom: "20px" }}>
            <strong>Требуемые роли:</strong>
            <div style={{ marginTop: "12px" }}>
              {project.roles.map((role, idx) => {
                const filled = members.filter(
                  (m) => m.role_name === role.name,
                ).length;
                return (
                  <div
                    key={idx}
                    style={{
                      background: "#f5f5f5",
                      borderRadius: "8px",
                      padding: "12px",
                      marginBottom: "8px",
                    }}
                  >
                    <div className="flex-between">
                      <strong>{role.name}</strong>
                      <span
                        style={{
                          color: filled >= role.count ? "#28a745" : "#666",
                        }}
                      >
                        {filled}/{role.count} чел.
                      </span>
                    </div>
                    {role.skills?.length > 0 && (
                      <div style={{ marginTop: "8px" }}>
                        {role.skills.map((skill, sidx) => (
                          <span key={sidx} className="tag">
                            {skill.name} ({skill.level}+)
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        <p style={{ color: "#666", fontSize: "14px" }}>
          Команда: {totalFilled}/{totalNeeded || "?"} • Владелец: User #
          {project.owner_id}
        </p>
      </div>

      {/* Members by role */}
      <div className="card">
        <div className="flex-between mb-20">
          <h2 style={{ marginBottom: 0 }}>Участники ({members.length})</h2>
          {isOwner && (
            <button
              className="secondary"
              onClick={() => setShowAddMember(!showAddMember)}
            >
              + Добавить вручную
            </button>
          )}
        </div>

        {showAddMember && isOwner && (
          <div
            style={{
              marginBottom: "20px",
              padding: "16px",
              background: "#f5f5f5",
              borderRadius: "8px",
            }}
          >
            <div className="flex" style={{ flexWrap: "wrap" }}>
              <select
                value={selectedUserId}
                onChange={(e) => setSelectedUserId(e.target.value)}
                style={{ flex: 1, minWidth: "200px" }}
              >
                <option value="">Выберите пользователя</option>
                {availableUsers.map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.name || u.username || `User #${u.id}`}
                  </option>
                ))}
              </select>
              {project.roles?.length > 0 && (
                <select
                  value={selectedRoleName}
                  onChange={(e) => setSelectedRoleName(e.target.value)}
                  style={{ flex: 1, minWidth: "150px" }}
                >
                  <option value="">Выберите роль</option>
                  {project.roles.map((r, idx) => (
                    <option key={idx} value={r.name}>
                      {r.name}
                    </option>
                  ))}
                </select>
              )}
              <button
                className="primary"
                onClick={handleAddMember}
                disabled={!selectedUserId}
              >
                Добавить
              </button>
            </div>
          </div>
        )}

        {Object.keys(membersByRole).length > 0 ? (
          Object.entries(membersByRole).map(([roleName, roleMembers]) => (
            <div key={roleName} style={{ marginBottom: "20px" }}>
              <h3
                style={{ borderBottom: "1px solid #eee", paddingBottom: "8px" }}
              >
                {roleName} ({roleMembers.length})
              </h3>
              <div className="grid grid-2">
                {roleMembers.map((member) => (
                  <UserCard
                    key={member.id}
                    user={member}
                    actions={
                      isOwner && (
                        <button
                          className="danger"
                          style={{ padding: "4px 10px", fontSize: "12px" }}
                          onClick={() => handleRemoveMember(member.id)}
                        >
                          Удалить
                        </button>
                      )
                    }
                  />
                ))}
              </div>
            </div>
          ))
        ) : (
          <p style={{ color: "#999" }}>Участников пока нет</p>
        )}
      </div>

      {/* AI Matching */}
      {isOwner && project.roles?.length > 0 && (
        <div className="card">
          <h2>🤖 AI Подбор команды</h2>
          <p style={{ color: "#666", marginBottom: "16px" }}>
            ИИ подберёт топ-3 лучших кандидатов на каждую роль
          </p>

          <button className="primary" onClick={handleMatch} disabled={matching}>
            {matching ? "Анализ..." : "Запустить подбор"}
          </button>

          {matchResults && (
            <div style={{ marginTop: "24px" }}>
              {matchResults.map((roleResult, idx) => (
                <div key={idx} style={{ marginBottom: "24px" }}>
                  <div
                    className="flex-between"
                    style={{ marginBottom: "12px" }}
                  >
                    <h3 style={{ margin: 0 }}>{roleResult.role_name}</h3>
                    <span
                      style={{
                        color:
                          roleResult.filled >= roleResult.needed
                            ? "#28a745"
                            : "#666",
                      }}
                    >
                      Заполнено: {roleResult.filled}/{roleResult.needed}
                    </span>
                  </div>

                  {roleResult.candidates.length === 0 ? (
                    <p style={{ color: "#999", fontStyle: "italic" }}>
                      Подходящих кандидатов не найдено
                    </p>
                  ) : (
                    <div>
                      {roleResult.candidates.map((candidate) => {
                        const userData = allUsers.find(
                          (u) => u.id === candidate.id,
                        );
                        const alreadyMember = memberIds.includes(candidate.id);

                        return (
                          <div
                            key={candidate.id}
                            style={{
                              padding: "16px",
                              background: "#f9f9f9",
                              borderRadius: "8px",
                              marginBottom: "12px",
                              borderLeft: `4px solid ${
                                candidate.score >= 70
                                  ? "#28a745"
                                  : candidate.score >= 40
                                    ? "#ffc107"
                                    : "#dc3545"
                              }`,
                            }}
                          >
                            <div className="flex-between">
                              <div style={{ flex: 1 }}>
                                <strong>
                                  <Link to={`/users/${candidate.id}`}>
                                    {userData?.name ||
                                      userData?.username ||
                                      `User #${candidate.id}`}
                                  </Link>
                                </strong>
                                <p
                                  style={{
                                    color: "#666",
                                    fontSize: "14px",
                                    marginTop: "4px",
                                  }}
                                >
                                  {candidate.reason}
                                </p>
                                {userData?.skills?.length > 0 && (
                                  <div style={{ marginTop: "8px" }}>
                                    {userData.skills.slice(0, 5).map((s, i) => (
                                      <span key={i} className="tag">
                                        {s.name} ({s.level})
                                      </span>
                                    ))}
                                  </div>
                                )}
                              </div>
                              <div
                                style={{
                                  textAlign: "right",
                                  marginLeft: "16px",
                                }}
                              >
                                <div
                                  style={{
                                    fontSize: "28px",
                                    fontWeight: "bold",
                                    color:
                                      candidate.score >= 70
                                        ? "#28a745"
                                        : candidate.score >= 40
                                          ? "#ffc107"
                                          : "#dc3545",
                                  }}
                                >
                                  {candidate.score}%
                                </div>
                                {!alreadyMember &&
                                  roleResult.filled < roleResult.needed && (
                                    <button
                                      className="primary"
                                      style={{
                                        marginTop: "8px",
                                        padding: "6px 12px",
                                        fontSize: "12px",
                                      }}
                                      onClick={() =>
                                        handleAddFromMatch(
                                          candidate.id,
                                          roleResult.role_name,
                                        )
                                      }
                                    >
                                      Добавить
                                    </button>
                                  )}
                                {alreadyMember && (
                                  <span
                                    style={{
                                      color: "#28a745",
                                      fontSize: "12px",
                                    }}
                                  >
                                    ✓ В команде
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {isOwner && (!project.roles || project.roles.length === 0) && (
        <div className="card" style={{ textAlign: "center" }}>
          <p style={{ color: "#666" }}>
            Добавьте роли в проект, чтобы использовать AI-подбор
          </p>
          <Link to={`/projects/${projectId}/edit`}>
            <button className="primary">Редактировать проект</button>
          </Link>
        </div>
      )}
    </Layout>
  );
}
