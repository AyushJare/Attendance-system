import { useState, useEffect } from 'react';
import { adminService } from '../services/api';
import './AdminPanel.css';

export default function AdminPanel() {
  const [suspicious, setSuspicious] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [actionMessage, setActionMessage] = useState('');

  useEffect(() => {
    fetchSuspicious();
  }, []);

  const fetchSuspicious = async () => {
    try {
      setLoading(true);
      setError('');
      setActionMessage('');
      const data = await adminService.getSuspiciousCheckIns();
      setSuspicious(data.records || []);
    } catch (err) {
      setError(`❌ Error loading records: ${err.message || 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id) => {
    try {
      await adminService.approveCheckIn(id);
      setActionMessage('✅ Check-in approved');
      setSuspicious(suspicious.filter((s) => s.id !== id));
      setTimeout(() => setActionMessage(''), 3000);
    } catch (err) {
      setError(`❌ Error approving: ${err.message}`);
    }
  };

  const handleReject = async (id) => {
    try {
      await adminService.rejectCheckIn(id);
      setActionMessage('❌ Check-in rejected');
      setSuspicious(suspicious.filter((s) => s.id !== id));
      setTimeout(() => setActionMessage(''), 3000);
    } catch (err) {
      setError(`❌ Error rejecting: ${err.message}`);
    }
  };

  return (
    <div className="admin-container">
      <span className="emoji"><h1>👨‍💼 Admin Panel - Suspicious Check-Ins</h1></span>

      <div className="admin-header">
        <p className="count">Total Flagged: <strong>{suspicious.length}</strong></p>
        <button onClick={fetchSuspicious} className="btn-refresh">
          🔄 Refresh
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}
      {actionMessage && <div className="success-message">{actionMessage}</div>}

      {loading ? (
        <p className="loading">Loading...</p>
      ) : suspicious.length === 0 ? (
        <p className="no-records">No flagged check-ins - All clear! ✓</p>
      ) : (
        <div className="flagged-list">
          {suspicious.map((record) => (
            <div key={record.id} className={`flagged-card severity-${record.severity}`}>
              <div className="card-header">
                <span className="record-id">Record #{record.attendance_record_id}</span>
                <span className={`severity-badge ${record.severity}`}>{record.severity.toUpperCase()}</span>
              </div>

              <div className="card-body">
                <p className="reason"><strong>Reason:</strong> {record.reason}</p>
                <p className="timestamp">
                  <strong>Flagged:</strong> {new Date(record.flagged_at).toLocaleString()}
                </p>
              </div>

              <div className="card-actions">
                <button
                  onClick={() => handleApprove(record.id)}
                  className="btn btn-approve"
                >
                  ✓ Approve
                </button>
                <button
                  onClick={() => handleReject(record.id)}
                  className="btn btn-reject"
                >
                  ✗ Reject
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}