import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const attendanceService = {
  checkIn: async (employeeId, latitude, longitude, gpsAccuracy, deviceId) => {
    try {
      const response = await api.post(
        '/attendance/check-in',
        {
          latitude,
          longitude,
          gps_accuracy: gpsAccuracy,
          device_id: deviceId,
          ip_address: null,
        },
        { params: { employee_id: employeeId } }
      );
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  checkOut: async (employeeId, latitude, longitude, gpsAccuracy, deviceId) => {
    try {
      const response = await api.post(
        '/attendance/check-out',
        {
          latitude,
          longitude,
          gps_accuracy: gpsAccuracy,
          device_id: deviceId,
          ip_address: null,
        },
        { params: { employee_id: employeeId } }
      );
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  getHistory: async (employeeId) => {
    try {
      const response = await api.get(`/attendance/history/${employeeId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  getOfficeLocations: async () => {
    try {
      const response = await api.get('/attendance/office-locations');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
};

export const adminService = {
  getSuspiciousCheckIns: async () => {
    try {
      const response = await api.get('/admin/suspicious-checkins');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  approveCheckIn: async (suspiciousId, notes = '') => {
    try {
      const response = await api.post(`/admin/approve/${suspiciousId}`, { notes });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  rejectCheckIn: async (suspiciousId, notes = '') => {
    try {
      const response = await api.post(`/admin/reject/${suspiciousId}`, { notes });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
};
