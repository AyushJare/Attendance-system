import { useState } from 'react';
import CheckInScreen from './components/CheckInScreen';
import HistoryScreen from './components/HistoryScreen';
import AdminPanel from './components/AdminPanel';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('checkin');
  const [role, setRole] = useState('employee'); // Add this line

  const toggleRole = () => {
    setRole(role === 'employee' ? 'admin' : 'employee');
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="header-top">
            <div>
              <h1><span className="emoji">🏢</span> Attendance Tracking System</h1>              
              <p className="tagline">Location-based check-in with GPS validation</p>
            </div>
            <div className="role-toggle">
              <span className="role-badge">{role.toUpperCase()}</span>
              <button 
                onClick={toggleRole}
                className="role-switch-btn"
              >
                👤 Switch to {role === 'employee' ? 'Admin' : 'Employee'}
              </button>
            </div>
          </div>
        </div>
      </header>

      <nav className="app-nav">
        <button
          className={`nav-btn ${activeTab === 'checkin' ? 'active' : ''}`}
          onClick={() => setActiveTab('checkin')}
        >
          📍 Check-In
        </button>
        <button
          className={`nav-btn ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          📋 History
        </button>
        
        {/* Only show Admin tab if role is admin */}
        {role === 'admin' && (
          <button
            className={`nav-btn ${activeTab === 'admin' ? 'active' : ''}`}
            onClick={() => setActiveTab('admin')}
          >
            👨‍💼 Admin
          </button>
        )}
      </nav>

      <main className="app-main">
        {activeTab === 'checkin' && <CheckInScreen role={role} />}
        {activeTab === 'history' && <HistoryScreen role={role} />}
        {activeTab === 'admin' && role === 'admin' && <AdminPanel />}
      </main>

      <footer className="app-footer">
        <p>Attendance Tracking System v1.0 | Backend: http://localhost:8000 | Role: {role.toUpperCase()}</p>
      </footer>
    </div>
  );
}

export default App;