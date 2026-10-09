const API_BASE = '/api';

export async function fetchApi(endpoint, options = {}, role = 'Station Officer', district = 'Pune') {
  const headers = {
    'Content-Type': 'application/json',
    'X-User-Role': role,
    'X-User-District': district,
    ...(options.headers || {})
  };

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || `API request failed with status ${response.status}`);
  }

  return response.json();
}

export const api = {
  getCases: (params = {}, role, district) => {
    const query = new URLSearchParams(params).toString();
    return fetchApi(`/cases${query ? `?${query}` : ''}`, {}, role, district);
  },
  getCaseById: (id, role, district) => fetchApi(`/cases/${id}`, {}, role, district),
  createCase: (data, role, district) => fetchApi('/cases', { method: 'POST', body: JSON.stringify(data) }, role, district),
  
  getMatchesForCase: (caseId, role, district) => fetchApi(`/matches/case/${caseId}`, {}, role, district),
  verifyMatch: (matchId, notes, role, district) => fetchApi(`/matches/${matchId}/verify`, { method: 'POST', body: JSON.stringify({ notes }) }, role, district),
  rejectMatch: (matchId, rejectionReason, role, district) => fetchApi(`/matches/${matchId}/reject`, { method: 'POST', body: JSON.stringify({ rejection_reason: rejectionReason }) }, role, district),

  getGraph: (role, district) => fetchApi('/graph', {}, role, district),
  getDashboard: (role, district) => fetchApi('/dashboard', {}, role, district),
  getAuditLogs: (role, district) => fetchApi('/audit', {}, role, district),
};
