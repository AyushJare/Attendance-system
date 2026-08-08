import { useState, useEffect } from 'react';
import { attendanceService } from '../services/api';
import { getLocation, calculateDistance } from '../services/locationService';
import './CheckInScreen.css';

export default function CheckInScreen({ role }) {
  const [location, setLocation] = useState(null);
  const [distance, setDistance] = useState(null);
  const [officeLocation, setOfficeLocation] = useState(null);
  const [officeLoading, setOfficeLoading] = useState(true);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('');
  const [message, setMessage] = useState('');

  // Use different employee ID based on role
  const EMPLOYEE_ID = role === 'admin' ? 2 : 1;

  // Fetch office location from backend
  useEffect(() => {
    const fetchOfficeLocation = async () => {
      try {
        setOfficeLoading(true);
        const response = await attendanceService.getOfficeLocations();
        setOfficeLocation(response.locations?.[0] || null);
      } catch (error) {
        setStatus('error');
        setMessage(`❌ Failed to load office location: ${error.message || 'Unknown error'}`);
      } finally {
        setOfficeLoading(false);
      }
    };

    fetchOfficeLocation();
  }, []);

  const handleGetLocation = async () => {
    try {
      setLoading(true);
      setMessage('');
      const loc = await getLocation();
      setLocation(loc);

      // Calculate distance using fetched office location
      if (officeLocation) {
        const dist = calculateDistance(
          officeLocation.latitude,
          officeLocation.longitude,
          loc.latitude,
          loc.longitude
        );
        setDistance(dist);
      }
    } catch (error) {
      setStatus('error');
      setMessage(`❌ ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCheckIn = async () => {
    let deviceId = localStorage.getItem('deviceId');
    if (!deviceId) {
      deviceId = 'device-' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('deviceId', deviceId);
    }

    if (!location) {
      setMessage('❌ Get location first');
      return;
    }

    try {
      setLoading(true);
      const response = await attendanceService.checkIn(
        EMPLOYEE_ID,
        location.latitude,
        location.longitude,
        location.accuracy,
        deviceId
      );

      if (response.success) {
        setStatus('success');
        setMessage('✅ ' + response.message);
      } else if (response.requires_approval) {
        setStatus('pending');
        setMessage('⏳ ' + response.message);
      } else {
        setStatus('error');
        setMessage('❌ ' + response.message);
      }
    } catch (error) {
      setStatus('error');
      setMessage(`❌ Error: ${error.message || 'Check-in failed'}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCheckOut = async () => {
    let deviceId = localStorage.getItem('deviceId');
    if (!deviceId) {
      deviceId = 'device-' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('deviceId', deviceId);
    }

    if (!location) {
      setMessage('❌ Get location first');
      return;
    }

    try {
      setLoading(true);
      const response = await attendanceService.checkOut(
        EMPLOYEE_ID,
        location.latitude,
        location.longitude,
        location.accuracy,
        deviceId
      );

      setStatus('success');
      setMessage('✅ ' + response.message);
    } catch (error) {
      setStatus('error');
      setMessage(`❌ Error: ${error.message || 'Check-out failed'}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="checkin-container">
      <span className="emoji"><h1>📍 Location-Based Check-In</h1></span>

      {officeLoading && <p className="loading">Loading office location...</p>}

      {location && (
        <div className="location-box">
          <h3>Current Location</h3>
          <p><strong>Latitude:</strong> {location.latitude.toFixed(6)}</p>
          <p><strong>Longitude:</strong> {location.longitude.toFixed(6)}</p>
          <p><strong>GPS Accuracy:</strong> {location.accuracy.toFixed(1)}m</p>
        </div>
      )}

      {distance !== null && officeLocation && (
        <div className={`distance-box ${distance <= officeLocation.radius_meters ? 'inside' : 'outside'}`}>
          <h3>Distance from Office: {distance.toFixed(2)}m</h3>
          {distance <= officeLocation.radius_meters ? (
            <p className="inside-text">✓ Within geofence ({officeLocation.radius_meters}m)</p>
          ) : (
            <p className="outside-text">✗ Outside geofence ({officeLocation.radius_meters}m)</p>
          )}
        </div>
      )}

      <div className="button-group">
        <button
          onClick={handleGetLocation}
          disabled={loading}
          className="btn btn-secondary"
        >
          🔄 {loading ? 'Getting Location...' : 'Get Location'}
        </button>

        <button
          onClick={handleCheckIn}
          disabled={loading || !location}
          className="btn btn-success"
        >
          ✓ {loading ? 'Checking In...' : 'Check In'}
        </button>

        <button
          onClick={handleCheckOut}
          disabled={loading || !location}
          className="btn btn-warning"
        >
          ✓ {loading ? 'Checking Out...' : 'Check Out'}
        </button>
      </div>

      {message && (
        <div className={`message-box ${status}`}>
          {message}
        </div>
      )}
    </div>
  );
}
