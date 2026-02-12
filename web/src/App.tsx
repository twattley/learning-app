import { NavLink, Outlet } from "react-router-dom";

export default function App() {
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
      </nav>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
