import { useState, useEffect } from 'react';
import { attendanceService } from '../services/api';
import './HistoryScreen.css';

export default function HistoryScreen({ role }) {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const EMPLOYEE_ID = role === 'admin' ? 2 : 1;
  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await attendanceService.getHistory(EMPLOYEE_ID);
      setRecords(data.records || []);
    } catch (err) {
      setError(`❌ Error loading history: ${err.message || 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="history-container">
      <span className="emoji"><h1>📋 Attendance History</h1></span>

      <button onClick={fetchHistory} className="btn-refresh">
        🔄 Refresh
      </button>

      {error && <div className="error-message">{error}</div>}

      {loading ? (
        <p className="loading">Loading...</p>
      ) : records.length === 0 ? (
        <p className="no-records">No attendance records found</p>
      ) : (
        <div className="records-list">
          {records.map((record) => (
            <div key={record.id} className="record-card">
              <div className="record-header">
                <span className="date">{record.date}</span>
                <span className={`status ${record.status.includes('valid') ? 'valid' : 'flagged'}`}>
                  {record.status}
                </span>
              </div>
              <div className="record-details">
                <p><strong>Check-in:</strong> {record.check_in}</p>
                <p><strong>Check-out:</strong> {record.check_out || 'N/A'}</p>
                <p><strong>Distance:</strong> {record.distance}m</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}