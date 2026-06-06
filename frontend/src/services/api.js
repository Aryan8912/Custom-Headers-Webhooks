import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// ── Axios instance ─────────────────────────────────────
const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// ── Auth headers from env ──────────────────────────────
// These match what Bolna sends to your webhook
const getAuthHeaders = () => ({
  Authorization: `Bearer ${import.meta.env.VITE_SECRET_KEY}`,
  "X-API-Key": import.meta.env.VITE_X_API_KEY,
  "X-Tenant-ID": import.meta.env.VITE_TENANT_ID || "tenant_a",
});

// ── Executions API ─────────────────────────────────────
export const executionsApi = {

  // GET /executions
  getAll: async ({ page = 1, pageSize = 20, agentId, status } = {}) => {
    const params = { page, page_size: pageSize };
    if (agentId) params.agent_id = agentId;
    if (status) params.status = status;

    const response = await api.get("/executions", {
      headers: getAuthHeaders(),
      params,
    });
    return response.data;
  },

  // GET /executions/:id
  getById: async (executionId) => {
    const response = await api.get(`/executions/${executionId}`, {
      headers: getAuthHeaders(),
    });
    return response.data;
  },
};

// ── Health API ─────────────────────────────────────────
export const healthApi = {
  check: async () => {
    const response = await api.get("/health");
    return response.data;
  },

  deepCheck: async () => {
    const response = await api.get("/health/deep");
    return response.data;
  },
};

export default api;