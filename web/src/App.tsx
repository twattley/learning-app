import { useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { getLLMMode, setLLMMode, type LLMMode } from "./lib/api";

export default function App() {
  const [llmMode, setMode] = useState<LLMMode | null>(null);
  const [switching, setSwitching] = useState(false);

  useEffect(() => {
    getLLMMode().then(setMode).catch(() => {});
  }, []);

  const handleToggle = async () => {
    if (!llmMode) return;
    setSwitching(true);
    try {
      const newMode = llmMode.mode === "local" ? "web" : "local";
      const result = await setLLMMode(newMode);
      setMode(result);
    } catch {
      // ignore
    } finally {
      setSwitching(false);
    }
  };

  return (
    <div className="app">
      <nav className="sidebar">
        <div className="logo">📚 Recall</div>
        <NavLink to="/" end className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
          🧠 Learn
        </NavLink>
        <NavLink to="/questions" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
          📝 Questions
        </NavLink>
        <div className="sidebar-spacer" />
        {llmMode && (
          <button
            className={`llm-toggle ${llmMode.mode}`}
            onClick={handleToggle}
            disabled={switching}
            title={`Using ${llmMode.provider} (${llmMode.model}). Click to switch.`}
          >
            <span className="llm-toggle-icon">
              {llmMode.mode === "local" ? "🏠" : "☁️"}
            </span>
            <span className="llm-toggle-label">
              {switching ? "…" : llmMode.mode === "local" ? "Local" : "Web"}
            </span>
            <span className="llm-toggle-model">{llmMode.model}</span>
          </button>
        )}
      </nav>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
