/**
 * API Helper
 * 
 * Automatically adds Authorization header to all requests
 */

const API_BASE_URL = 'http://localhost:8000/api';

/**
 * Get auth headers with token
 */
const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  
  const headers = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  return headers;
};

/**
 * Handle API response
 */
const handleResponse = async (response) => {
  if (response.status === 401) {
    // Token expired or invalid
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.reload(); // Force re-auth
    throw new Error('Session expired. Please log in again.');
  }

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Request failed');
  }

  return response.json();
};

/**
 * API methods
 */
export const api = {
  // Execute multi-agent task
  runAgent: async (userGoal) => {
    const response = await fetch(`${API_BASE_URL}/run`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ user_goal: userGoal })
    });
    return handleResponse(response);
  },

  // List user's sessions
  getSessions: async (limit = 50) => {
    const response = await fetch(`${API_BASE_URL}/sessions/?limit=${limit}`, {
      headers: getAuthHeaders()
    });
    return handleResponse(response);
  },

  // Get specific session
  getSession: async (sessionId) => {
    const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}`, {
      headers: getAuthHeaders()
    });
    return handleResponse(response);
  },

  // Update session
  updateSession: async (sessionId, title) => {
    const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify({ title })
    });
    return handleResponse(response);
  },

  // Delete session
  deleteSession: async (sessionId) => {
    const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    return handleResponse(response);
  },

  // Get current user
  getCurrentUser: async () => {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: getAuthHeaders()
    });
    return handleResponse(response);
  }
};

export default api;