/**
 * ConsentHub Dashboard – main application logic.
 */

// ── State ──────────────────────────────────────────────────────────────────
const state = {
  user: null,
  currentPage: "dashboard",
  recordsPage: 1,
  policiesPage: 1,
};

// ── Toast ──────────────────────────────────────────────────────────────────
function toast(message, type = "info") {
  const container = document.getElementById("toastContainer");
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.innerHTML = `<span>${message}</span>`;
  container.appendChild(el);
  setTimeout(() => el.remove(), 4000);
}

// ── Auth ───────────────────────────────────────────────────────────────────
function isLoggedIn() {
  return !!localStorage.getItem("ch_access_token");
}

function storeAuth(data) {
  localStorage.setItem("ch_access_token", data.access_token);
  localStorage.setItem("ch_refresh_token", data.refresh_token);
  localStorage.setItem("ch_user", JSON.stringify(data.user));
  state.user = data.user;
}

function logout() {
  localStorage.clear();
  window.location.reload();
}

// ── Navigation ─────────────────────────────────────────────────────────────
function navigate(page) {
  document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));

  const pageEl = document.getElementById(`page-${page}`);
  if (pageEl) pageEl.classList.add("active");

  const navEl = document.querySelector(`[data-nav="${page}"]`);
  if (navEl) navEl.classList.add("active");

  document.getElementById("topbarTitle").textContent = {
    dashboard: "Dashboard",
    policies: "Consent Policies",
    records: "Consent Records",
    organizations: "Organizations",
    analytics: "Analytics",
  }[page] || "ConsentHub";

  state.currentPage = page;

  if (page === "dashboard") loadDashboard();
  if (page === "policies")  loadPolicies();
  if (page === "records")   loadRecords();
  if (page === "organizations") loadOrganizations();
  if (page === "analytics") loadAnalytics();
}

// ── Dashboard ──────────────────────────────────────────────────────────────
async function loadDashboard() {
  try {
    const [summary, health] = await Promise.all([
      api.analytics.summary(),
      api.health(),
    ]);

    setValue("stat-total",   summary.total_records ?? 0);
    setValue("stat-granted", summary.by_status?.granted ?? 0);
    setValue("stat-denied",  summary.by_status?.denied  ?? 0);
    setValue("stat-rate",    (summary.consent_rate_pct ?? 0) + "%");
    setValue("stat-db",      health.database === "ok" ? "✅ OK" : "⚠ " + health.database);
    setValue("stat-version", health.version ?? "—");

    // Policy type breakdown
    const byMethod = summary.by_method || {};
    setValue("stat-web",  byMethod["web-form"] ?? 0);
    setValue("stat-api",  byMethod["api"] ?? 0);
    setValue("stat-email",byMethod["email"] ?? 0);

    // Mini trend chart
    const trends = await api.analytics.trends(7);
    renderMiniChart(trends.trends);
  } catch (e) {
    toast("Failed to load dashboard: " + (e.error || e.message || "Unknown error"), "error");
  }
}

function renderMiniChart(trends) {
  const canvas = document.getElementById("trendChart");
  if (!canvas || !window.Chart) return;

  const labels = trends.map(t => t.date);
  const granted = trends.map(t => t.granted || 0);
  const denied  = trends.map(t => t.denied  || 0);

  if (window._trendChart) window._trendChart.destroy();
  window._trendChart = new Chart(canvas.getContext("2d"), {
    type: "bar",
    data: {
      labels,
      datasets: [
        { label: "Granted", data: granted, backgroundColor: "#16a34a88", borderColor: "#16a34a", borderWidth: 1 },
        { label: "Denied",  data: denied,  backgroundColor: "#dc262688", borderColor: "#dc2626", borderWidth: 1 },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: "bottom" } },
      scales: { x: { stacked: false }, y: { beginAtZero: true, ticks: { stepSize: 1 } } },
    },
  });
}

// ── Policies ───────────────────────────────────────────────────────────────
async function loadPolicies(page = 1) {
  state.policiesPage = page;
  const tbody = document.getElementById("policiesTbody");
  tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:24px;color:#64748b">Loading…</td></tr>`;

  try {
    const data = await api.policies.list({ page, per_page: 15 });
    if (!data.items.length) {
      tbody.innerHTML = `<tr><td colspan="7"><div class="empty-state"><div class="icon">📋</div><p>No policies yet. Create your first policy.</p></div></td></tr>`;
      return;
    }
    tbody.innerHTML = data.items.map(p => `
      <tr>
        <td><strong>${esc(p.name)}</strong><br><small style="color:#64748b">${esc(p.id.slice(0,8))}…</small></td>
        <td><span class="badge badge-${p.policy_type}">${p.policy_type.toUpperCase()}</span></td>
        <td>v${esc(p.version)}</td>
        <td>${p.requires_explicit_consent ? "✅" : "❌"}</td>
        <td>${p.retention_days} days</td>
        <td><span class="badge ${p.is_active ? "badge-active" : "badge-inactive"}">${p.is_active ? "Active" : "Inactive"}</span></td>
        <td>
          <button class="btn btn-sm btn-secondary" onclick="openEditPolicy('${p.id}')">Edit</button>
          <button class="btn btn-sm btn-danger" onclick="deletePolicy('${p.id}')">Delete</button>
        </td>
      </tr>
    `).join("");
    renderPagination("policiesPagination", data, loadPolicies);
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="7" style="color:#dc2626;padding:16px">Error loading policies</td></tr>`;
    toast("Error loading policies", "error");
  }
}

async function deletePolicy(id) {
  if (!confirm("Deactivate this policy?")) return;
  try {
    await api.policies.delete(id);
    toast("Policy deactivated", "success");
    loadPolicies(state.policiesPage);
  } catch (e) {
    toast("Failed to delete policy", "error");
  }
}

// Policy modal
const policyModal = {
  open(mode = "create", data = {}) {
    document.getElementById("policyModalTitle").textContent = mode === "edit" ? "Edit Policy" : "New Consent Policy";
    document.getElementById("policyForm").reset();
    document.getElementById("policyModalMode").value = mode;
    document.getElementById("policyModalId").value = data.id || "";
    if (mode === "edit") {
      document.getElementById("policyName").value = data.name || "";
      document.getElementById("policyType").value = data.policy_type || "gdpr";
      document.getElementById("policyDesc").value = data.description || "";
      document.getElementById("policyVersion").value = data.version || "1.0";
      document.getElementById("policyRetention").value = data.retention_days || 365;
      document.getElementById("policyExplicit").checked = !!data.requires_explicit_consent;
    }
    document.getElementById("policyModal").classList.add("open");
  },
  close() { document.getElementById("policyModal").classList.remove("open"); },
};

async function openEditPolicy(id) {
  try {
    const p = await api.request("GET", `/consents/policies/${id}`);
    policyModal.open("edit", p);
  } catch { toast("Failed to load policy", "error"); }
}

async function submitPolicyForm(e) {
  e.preventDefault();
  const mode = document.getElementById("policyModalMode").value;
  const id   = document.getElementById("policyModalId").value;
  const body = {
    name: document.getElementById("policyName").value,
    policy_type: document.getElementById("policyType").value,
    description: document.getElementById("policyDesc").value,
    version: document.getElementById("policyVersion").value,
    retention_days: parseInt(document.getElementById("policyRetention").value),
    requires_explicit_consent: document.getElementById("policyExplicit").checked,
  };
  if (state.user?.organization_id) body.organization_id = state.user.organization_id;

  try {
    if (mode === "edit") {
      await api.policies.update(id, body);
      toast("Policy updated", "success");
    } else {
      await api.policies.create(body);
      toast("Policy created", "success");
    }
    policyModal.close();
    loadPolicies(state.policiesPage);
  } catch (e) {
    toast("Save failed: " + (e.error || e.message || ""), "error");
  }
}

// ── Records ────────────────────────────────────────────────────────────────
async function loadRecords(page = 1) {
  state.recordsPage = page;
  const tbody = document.getElementById("recordsTbody");
  tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:24px;color:#64748b">Loading…</td></tr>`;

  const params = { page, per_page: 15 };
  const statusFilter = document.getElementById("recordStatusFilter")?.value;
  if (statusFilter) params.status = statusFilter;

  try {
    const data = await api.records.list(params);
    if (!data.items.length) {
      tbody.innerHTML = `<tr><td colspan="7"><div class="empty-state"><div class="icon">📄</div><p>No consent records found.</p></div></td></tr>`;
      return;
    }
    tbody.innerHTML = data.items.map(r => `
      <tr>
        <td><code style="font-size:.78rem">${r.id ? esc(r.id.slice(0,8)) + '…' : '—'}</code></td>
        <td>${esc(r.data_subject_email || r.data_subject_id)}</td>
        <td><code style="font-size:.78rem">${r.policy_id ? esc(r.policy_id.slice(0,8)) + '…' : '—'}</code></td>
        <td><span class="badge badge-${r.status}">${r.status}</span></td>
        <td>${r.consent_method || "—"}</td>
        <td>${r.granted_at ? new Date(r.granted_at).toLocaleDateString() : "—"}</td>
        <td>
          ${r.status === "granted"
            ? `<button class="btn btn-sm btn-danger" onclick="withdrawRecord('${r.id}')">Withdraw</button>`
            : `<span style="color:#94a3b8;font-size:.78rem">${r.status}</span>`}
        </td>
      </tr>
    `).join("");
    renderPagination("recordsPagination", data, loadRecords);
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="7" style="color:#dc2626;padding:16px">Error loading records</td></tr>`;
  }
}

async function withdrawRecord(id) {
  if (!confirm("Withdraw this consent?")) return;
  try {
    await api.records.withdraw(id);
    toast("Consent withdrawn", "success");
    loadRecords(state.recordsPage);
  } catch (e) {
    toast("Withdraw failed", "error");
  }
}

// Record modal
const recordModal = {
  open() { document.getElementById("recordModal").classList.add("open"); },
  close() { document.getElementById("recordModal").classList.remove("open"); },
};

async function submitRecordForm(e) {
  e.preventDefault();
  const body = {
    policy_id:          document.getElementById("recPolicyId").value,
    data_subject_id:    document.getElementById("recSubjectId").value,
    data_subject_email: document.getElementById("recSubjectEmail").value,
    status:             document.getElementById("recStatus").value,
    consent_method:     document.getElementById("recMethod").value,
  };
  try {
    await api.records.create(body);
    toast("Consent record created", "success");
    recordModal.close();
    document.getElementById("recordForm").reset();
    loadRecords(state.recordsPage);
  } catch (e) {
    toast("Failed to create record: " + (e.error || ""), "error");
  }
}

// Populate policy dropdown in record modal
async function populatePolicySelect() {
  try {
    const data = await api.policies.list({ is_active: "true", per_page: 100 });
    const sel  = document.getElementById("recPolicyId");
    sel.innerHTML = data.items.map(p =>
      `<option value="${p.id}">${esc(p.name)} (${p.policy_type})</option>`
    ).join("");
  } catch {}
}

// ── Organizations ──────────────────────────────────────────────────────────
async function loadOrganizations(page = 1) {
  if (state.user?.role !== "admin") {
    document.getElementById("page-organizations").innerHTML =
      `<div class="card"><p style="color:#dc2626">Admin access required.</p></div>`;
    return;
  }
  const tbody = document.getElementById("orgsTbody");
  if (!tbody) return;
  tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;padding:24px;color:#64748b">Loading…</td></tr>`;
  try {
    const data = await api.orgs.list({ page, per_page: 15 });
    if (!data.items.length) {
      tbody.innerHTML = `<tr><td colspan="5"><div class="empty-state"><div class="icon">🏢</div><p>No organizations yet.</p></div></td></tr>`;
      return;
    }
    tbody.innerHTML = data.items.map(o => `
      <tr>
        <td><strong>${esc(o.name)}</strong></td>
        <td>${esc(o.domain)}</td>
        <td>${esc(o.industry || "—")}</td>
        <td><span class="badge badge-${o.plan === "free" ? "inactive" : "active"}">${o.plan}</span></td>
        <td><span class="badge ${o.is_active ? "badge-active" : "badge-inactive"}">${o.is_active ? "Active" : "Inactive"}</span></td>
      </tr>
    `).join("");
    renderPagination("orgsPagination", data, loadOrganizations);
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="5" style="color:#dc2626;padding:16px">Error</td></tr>`;
  }
}

// ── Analytics ──────────────────────────────────────────────────────────────
async function loadAnalytics() {
  try {
    const [summary, trends] = await Promise.all([
      api.analytics.summary(),
      api.analytics.trends(30),
    ]);

    setValue("an-total",   summary.total_records ?? 0);
    setValue("an-rate",    (summary.consent_rate_pct ?? 0) + "%");
    setValue("an-granted", summary.by_status?.granted ?? 0);
    setValue("an-denied",  summary.by_status?.denied  ?? 0);
    setValue("an-withdrawn",summary.by_status?.withdrawn ?? 0);

    renderTrendChart(trends.trends);
    renderMethodChart(summary.by_method || {});
  } catch (e) {
    toast("Failed to load analytics", "error");
  }
}

function renderTrendChart(trends) {
  const canvas = document.getElementById("analyticsChart");
  if (!canvas || !window.Chart) return;
  const labels  = trends.map(t => t.date);
  const granted = trends.map(t => t.granted || 0);
  const denied  = trends.map(t => t.denied  || 0);
  if (window._analyticsChart) window._analyticsChart.destroy();
  window._analyticsChart = new Chart(canvas.getContext("2d"), {
    type: "line",
    data: {
      labels,
      datasets: [
        { label: "Granted", data: granted, borderColor: "#16a34a", backgroundColor: "#16a34a22", tension: .4, fill: true },
        { label: "Denied",  data: denied,  borderColor: "#dc2626", backgroundColor: "#dc262622", tension: .4, fill: true },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: "bottom" } },
      scales: { y: { beginAtZero: true } },
    },
  });
}

function renderMethodChart(byMethod) {
  const canvas = document.getElementById("methodChart");
  if (!canvas || !window.Chart) return;
  const labels = Object.keys(byMethod);
  const values = Object.values(byMethod);
  if (window._methodChart) window._methodChart.destroy();
  window._methodChart = new Chart(canvas.getContext("2d"), {
    type: "doughnut",
    data: {
      labels,
      datasets: [{ data: values, backgroundColor: ["#3b82f6","#16a34a","#d97706","#8b5cf6","#ef4444"] }],
    },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: "bottom" } } },
  });
}

// ── Helpers ─────────────────────────────────────────────────────────────────
function setValue(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function esc(str) {
  return String(str ?? "").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}

function renderPagination(containerId, data, loadFn) {
  const el = document.getElementById(containerId);
  if (!el) return;
  const { page, pages } = data;
  let html = `<button class="page-btn" ${page <= 1 ? "disabled" : ""} onclick="${loadFn.name}(${page-1})">←</button>`;
  for (let i = Math.max(1, page-2); i <= Math.min(pages, page+2); i++) {
    html += `<button class="page-btn ${i===page?"active":""}" onclick="${loadFn.name}(${i})">${i}</button>`;
  }
  html += `<button class="page-btn" ${page >= pages ? "disabled" : ""} onclick="${loadFn.name}(${page+1})">→</button>`;
  html += `<span style="color:#64748b;font-size:.8rem">Page ${page} of ${pages} (${data.total} total)</span>`;
  el.innerHTML = html;
}

// ── Export helpers ──────────────────────────────────────────────────────────
function exportRecordsCsv() {
  const url = `${API_BASE}/consents/records/export?format=csv`;
  const token = localStorage.getItem("ch_access_token");
  fetch(url, { headers: { Authorization: `Bearer ${token}` } })
    .then(r => r.blob())
    .then(blob => {
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = `consent_records_${Date.now()}.csv`;
      a.click();
    })
    .catch(() => toast("Export failed", "error"));
}

function exportRecordsJson() {
  const url = `${API_BASE}/consents/records/export?format=json`;
  const token = localStorage.getItem("ch_access_token");
  fetch(url, { headers: { Authorization: `Bearer ${token}` } })
    .then(r => r.blob())
    .then(blob => {
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = `consent_records_${Date.now()}.json`;
      a.click();
    })
    .catch(() => toast("Export failed", "error"));
}

// ── Boot ──────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", async () => {
  // Wire login form
  const loginForm = document.getElementById("loginForm");
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const email    = document.getElementById("loginEmail").value;
      const password = document.getElementById("loginPassword").value;
      const btn      = document.getElementById("loginBtn");
      btn.disabled = true;
      btn.textContent = "Signing in…";
      try {
        const data = await api.auth.login(email, password);
        storeAuth(data);
        window.location.reload();
      } catch (err) {
        toast("Login failed: " + (err.error || "Invalid credentials"), "error");
        btn.disabled = false;
        btn.textContent = "Sign In";
      }
    });
  }

  if (!isLoggedIn()) return;

  // Load user
  try {
    const stored = localStorage.getItem("ch_user");
    state.user = stored ? JSON.parse(stored) : await api.auth.me();
    document.getElementById("userEmail").textContent = state.user.name || state.user.email;
    document.getElementById("userRole").textContent  = state.user.role;
    if (state.user.role !== "admin") {
      document.querySelectorAll("[data-admin-only]").forEach(el => el.style.display = "none");
    }
  } catch {}

  // Wire nav
  document.querySelectorAll("[data-nav]").forEach(el => {
    el.addEventListener("click", () => navigate(el.dataset.nav));
  });

  // Wire logout
  document.getElementById("logoutBtn")?.addEventListener("click", logout);

  // Wire policy form
  document.getElementById("policyForm")?.addEventListener("submit", submitPolicyForm);
  document.getElementById("openCreatePolicy")?.addEventListener("click", () => policyModal.open("create"));
  document.getElementById("closePolicyModal")?.addEventListener("click", policyModal.close);
  document.getElementById("cancelPolicyModal")?.addEventListener("click", policyModal.close);

  // Wire record form
  document.getElementById("recordForm")?.addEventListener("submit", submitRecordForm);
  document.getElementById("openCreateRecord")?.addEventListener("click", () => {
    populatePolicySelect();
    recordModal.open();
  });
  document.getElementById("closeRecordModal")?.addEventListener("click", recordModal.close);
  document.getElementById("cancelRecordModal")?.addEventListener("click", recordModal.close);

  // Wire record status filter
  document.getElementById("recordStatusFilter")?.addEventListener("change", () => loadRecords(1));

  // Initial page
  navigate("dashboard");
});
