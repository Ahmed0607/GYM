import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
});

// ─── Members List & Search ──────────────────────────────────────────────────

export const listMembers = async (query = '') => {
  const params = query ? { q: query } : {};
  const response = await api.get('/members/', { params });
  return response.data;
};

export const searchMembers = async (query) => {
  const response = await api.get(`/members/search?q=${query}`);
  return response.data;
};

// ─── Single Member ──────────────────────────────────────────────────────────

export const getMember = async (memberId) => {
  const response = await api.get(`/members/${memberId}`);
  return response.data;
};

export const updateMember = async (memberId, data) => {
  const response = await api.put(`/members/${memberId}`, data);
  return response.data;
};

export const deleteMember = async (memberId) => {
  const response = await api.delete(`/members/${memberId}`);
  return response.data;
};

export const deleteExpiredMembers = async () => {
  const response = await api.delete('/members/expired/all');
  return response.data;
};

// ─── Financial Operations ───────────────────────────────────────────────────

export const payDebt = async (memberId, amount) => {
  const response = await api.post(`/members/${memberId}/pay-debt`, { amount });
  return response.data;
};

export const updateSubscription = async (memberId, data) => {
  const response = await api.put(`/members/${memberId}/subscription`, data);
  return response.data;
};

// ─── Check-in ───────────────────────────────────────────────────────────────

export const checkinMember = async (memberId) => {
  const response = await api.post(`/members/${memberId}/checkin`);
  return response.data;
};

export const consumeAddon = async (memberId, addonName) => {
  const response = await api.post(`/members/${memberId}/consume-addon`, { addon_name: addonName });
  return response.data;
};


// ─── Onboarding ─────────────────────────────────────────────────────────────

export const createMember = async (memberData) => {
  const response = await api.post('/members/', memberData);
  return response.data;
};

// ─── Admin ──────────────────────────────────────────────────────────────────

export const getDashboard = async () => {
  const response = await api.get('/admin/dashboard');
  return response.data;
};

export const adminReset = async () => {
  const response = await api.delete('/admin/reset');
  return response.data;
};

// ─── Package Rules (Admin) ──────────────────────────────────────────────────

export const listPackages = async () => {
  const response = await api.get('/admin/packages');
  return response.data;
};

export const createPackage = async (data) => {
  const response = await api.post('/admin/packages', data);
  return response.data;
};

export const updatePackage = async (pkgId, data) => {
  const response = await api.put(`/admin/packages/${pkgId}`, data);
  return response.data;
};

export const deletePackage = async (pkgId) => {
  const response = await api.delete(`/admin/packages/${pkgId}`);
  return response.data;
};

// ─── Receptionists (Admin) ──────────────────────────────────────────────────

export const listReceptionists = async () => {
  const response = await api.get('/admin/receptionists');
  return response.data;
};

export const createReceptionist = async (data) => {
  const response = await api.post('/admin/receptionists', data);
  return response.data;
};

export const updateReceptionist = async (recId, data) => {
  const response = await api.put(`/admin/receptionists/${recId}`, data);
  return response.data;
};

export const deleteReceptionist = async (recId) => {
  const response = await api.delete(`/admin/receptionists/${recId}`);
  return response.data;
};

// ─── Freeze / Unfreeze ──────────────────────────────────────────────────────

export const freezeMember = async (memberId, duration_weeks = 2) => {
  const response = await api.post(`/members/${memberId}/freeze`, { duration_weeks });
  return response.data;
};

export const unfreezeMember = async (memberId) => {
  const response = await api.post(`/members/${memberId}/unfreeze`);
  return response.data;
};

// ─── Mock Time ──────────────────────────────────────────────────────────────

export const getMockTime = async () => {
  const response = await api.get('/admin/mock-time');
  return response.data;
};

export const setMockTime = async (target_date) => {
  const response = await api.post(`/admin/mock-time?target_date=${encodeURIComponent(target_date)}`);
  return response.data;
};

export const toggleMockTime = async (enabled) => {
  const response = await api.post(`/admin/mock-time/toggle?enabled=${enabled}`);
  return response.data;
};

// ─── Finances ───────────────────────────────────────────────────────────────

export const listStaff = async () => {
  const response = await api.get('/admin/staff');
  return response.data;
};

export const createStaff = async (data) => {
  const response = await api.post('/admin/staff', data);
  return response.data;
};

export const updateStaffPending = async (staffId, data) => {
  const response = await api.put(`/admin/staff/${staffId}/pending`, data);
  return response.data;
};

export const deleteStaff = async (staffId) => {
  const response = await api.delete(`/admin/staff/${staffId}`);
  return response.data;
};

export const createExpense = async (data) => {
  const response = await api.post('/admin/expenses', data);
  return response.data;
};

export const getFilteredFinances = async (startDate, endDate) => {
  const response = await api.get(`/admin/finances/filter?start_date=${encodeURIComponent(startDate)}&end_date=${encodeURIComponent(endDate)}`);
  return response.data;
};

export const verifyPin = async (pin) => {
  const response = await api.post('/auth/verify-pin', { pin });
  return response.data;
};

export const updatePin = async (new_pin) => {
  const response = await api.put('/admin/pin', { new_pin });
  return response.data;
};

// ─── Single Sessions ────────────────────────────────────────────────────────
export const createSingleSession = async (name, amount) => {
  const response = await api.post('/single-sessions', { name, amount });
  return response.data;
};

export const getSingleSessionPrice = async () => {
  const response = await api.get('/config/single-session-price');
  return response.data.price;
};

export const updateSingleSessionPrice = async (price) => {
  const response = await api.post('/config/single-session-price', { price });
  return response.data;
};

export const verifyAdminPassword = async (password) => {
  const response = await api.post('/verify_admin_password', { password });
  return response.data;
};

export const updateAdminPassword = async (old_password, new_password) => {
  const response = await api.put('/admin_password', { old_password, new_password });
  return response.data;
};