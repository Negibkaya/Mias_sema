import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { loginWithCode } from "../api/auth";

export default function Login() {
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const data = await loginWithCode(code.trim());
      login(data.access_token);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || "Неверный или просроченный код");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "20px",
      }}
    >
      <div className="card" style={{ maxWidth: "400px", width: "100%" }}>
        <h1 style={{ textAlign: "center", marginBottom: "8px" }}>
          🚀 TeamMatch
        </h1>
        <p style={{ textAlign: "center", color: "#666", marginBottom: "24px" }}>
          Вход через Telegram
        </p>

        <div
          style={{
            background: "#f0f7ff",
            padding: "16px",
            borderRadius: "8px",
            marginBottom: "24px",
          }}
        >
          <p style={{ fontSize: "14px", marginBottom: "8px" }}>
            <strong>Как получить код:</strong>
          </p>
          <ol style={{ fontSize: "14px", paddingLeft: "20px", color: "#555" }}>
            <li>Откройте Telegram бота</li>
            <li>
              Отправьте команду <code>/login</code>
            </li>
            <li>Скопируйте полученный код</li>
          </ol>
        </div>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Код из Telegram</label>
            <input
              type="text"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="Например: a1b2c3"
              autoFocus
              required
            />
          </div>

          <button
            type="submit"
            className="primary"
            disabled={loading || !code.trim()}
            style={{ width: "100%" }}
          >
            {loading ? "Проверка..." : "Войти"}
          </button>
        </form>
      </div>
    </div>
  );
}
