import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { useLLMMode, useSetLLMMode } from "./api/hooks";

export default function App() {
  const { data: llmMode } = useLLMMode();
  const setLLMModeMutation = useSetLLMMode();
  const [switching, setSwitching] = useState(false);

  const handleToggle = async () => {
    if (!llmMode) return;
    setSwitching(true);
    try {
      const newMode = llmMode.mode === "local" ? "web" : "local";
      await setLLMModeMutation.mutateAsync(newMode);
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
        <NavLink
          to="/"
          end
          className={({ isActive }) =>
            isActive ? "nav-link active" : "nav-link"
          }
        >
          🧠 Learn
        </NavLink>
        <NavLink
          to="/questions"
          className={({ isActive }) =>
            isActive ? "nav-link active" : "nav-link"
          }
        >
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
