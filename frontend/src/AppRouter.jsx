import { Routes, Route, Link, useLocation } from 'react-router-dom';
import Dashboard from './Dashboard.jsx';
import ModelsPage from './ModelsPage.jsx';
import './App.css';

function NavLink({ to, children }) {
  const location = useLocation();
  const isActive = location.pathname === to;
  return (
    <Link to={to} className={`nav-link ${isActive ? 'active' : ''}`}>
      {children}
    </Link>
  );
}

export default function App() {
  return (
    <div className="app-shell">
      <nav className="app-nav">
        <div className="nav-brand">
          <span className="nav-icon">🏈</span>
          <span className="nav-title">NFL Predictor</span>
        </div>
        <div className="nav-links">
          <NavLink to="/">📊 Dashboard</NavLink>
          <NavLink to="/models">🤖 Models</NavLink>
        </div>
      </nav>

      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/models" element={<ModelsPage />} />
      </Routes>
    </div>
  );
}
