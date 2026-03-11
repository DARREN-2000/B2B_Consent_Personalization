/**
 * ConsentHub API client.
 * All API calls go through this module so auth headers & base URL are centralized.
 */

const API_BASE = window.CONSENTHUB_API_URL || "http://localhost:5000/api";

const api = {
  _getToken() {
    return localStorage.getItem("ch_access_token");
  },

  _headers(extra = {}) {
    const h = { "Content-Type": "application/json", ...extra };
    const t = this._getToken();
    if (t) h["Authorization"] = `Bearer ${t}`;
    return h;
  },

  async request(method, path, body = null, extraHeaders = {}) {
    const opts = {
      method,
      headers: this._headers(extraHeaders),
    };
    if (body) opts.body = JSON.stringify(body);

    const resp = await fetch(`${API_BASE}${path}`, opts);

    // Handle 401 → redirect to login
    if (resp.status === 401) {
      localStorage.removeItem("ch_access_token");
      localStorage.removeItem("ch_refresh_token");
      localStorage.removeItem("ch_user");
      window.location.reload();
      return;
    }

    const data = await resp.json().catch(() => ({}));
    if (!resp.ok) throw { status: resp.status, ...data };
    return data;
  },

  get:    (path, params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return api.request("GET", qs ? `${path}?${qs}` : path);
  },
  post:   (path, body) => api.request("POST", path, body),
  put:    (path, body) => api.request("PUT", path, body),
  delete: (path)       => api.request("DELETE", path),

  // ── Auth ────────────────────────────────────────────────────────────────
  auth: {
    login:   (email, password) => api.post("/auth/login", { email, password }),
    me:      ()                => api.get("/auth/me"),
    refresh: (token) => api.request("POST", "/auth/refresh", null,
      { Authorization: `Bearer ${token}` }),
  },

  // ── Organizations ────────────────────────────────────────────────────────
  orgs: {
    list:   (p = {}) => api.get("/organizations", p),
    create: (d)      => api.post("/organizations", d),
    update: (id, d)  => api.put(`/organizations/${id}`, d),
    delete: (id)     => api.delete(`/organizations/${id}`),
  },

  // ── Consent Policies ─────────────────────────────────────────────────────
  policies: {
    list:   (p = {}) => api.get("/consents/policies", p),
    create: (d)      => api.post("/consents/policies", d),
    update: (id, d)  => api.put(`/consents/policies/${id}`, d),
    delete: (id)     => api.delete(`/consents/policies/${id}`),
  },

  // ── Consent Records ──────────────────────────────────────────────────────
  records: {
    list:     (p = {}) => api.get("/consents/records", p),
    create:   (d)      => api.post("/consents/records", d),
    withdraw: (id)     => api.put(`/consents/records/${id}/withdraw`),
    exportCsv: ()      => `${API_BASE}/consents/records/export?format=csv`,
    exportJson: ()     => `${API_BASE}/consents/records/export?format=json`,
  },

  // ── Analytics ────────────────────────────────────────────────────────────
  analytics: {
    summary:  ()        => api.get("/analytics/summary"),
    trends:   (days=30) => api.get("/analytics/trends", { days }),
    overview: ()        => api.get("/analytics/overview"),
  },

  // ── Health ────────────────────────────────────────────────────────────────
  health: () => api.get("/health"),
};
