import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div>
      <nav
        style={{
          background: "white",
          padding: "16px 24px",
          boxShadow: "0 2px 4px rgba(0,0,0,0.08)",
          marginBottom: "24px",
        }}
      >
        <div
          style={{
            maxWidth: "1200px",
            margin: "0 auto",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div className="flex" style={{ gap: "24px" }}>
            <Link
              to="/"
              style={{ fontWeight: "bold", fontSize: "18px", color: "#333" }}
            >
              🚀 TeamMatch
            </Link>
            <Link to="/projects">Проекты</Link>
            <Link to="/users">Пользователи</Link>
          </div>

          <div className="flex">
            <Link to="/profile" style={{ marginRight: "16px" }}>
              👤 {user?.name || user?.username || "Профиль"}
            </Link>
            <button
              onClick={handleLogout}
              className="secondary"
              style={{ padding: "6px 12px" }}
            >
              Выйти
            </button>
          </div>
        </div>
      </nav>

      <main className="container">{children}</main>
    </div>
  );
}
