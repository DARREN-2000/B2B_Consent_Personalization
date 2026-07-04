// A mock API to allow the dashboard to function without a real backend for GitHub Pages.
// This intercepts fetch calls if the user selects "Demo Mode".

let MOCK_DATA = {
  policies: [
    { id: 'pol_1', name: 'GDPR Marketing Consent', policy_type: 'gdpr', version: '1.0', retention_days: 365, requires_explicit_consent: true, is_active: true },
    { id: 'pol_2', name: 'CCPA Do Not Sell', policy_type: 'ccpa', version: '1.0', retention_days: 180, requires_explicit_consent: false, is_active: true },
  ],
  records: [
    { id: 'rec_1', data_subject_id: 'user-123', policy: { name: 'GDPR Marketing Consent' }, status: 'granted', consent_method: 'web-form', granted_at: new Date().toISOString() },
    { id: 'rec_2', data_subject_id: 'user-456', policy: { name: 'CCPA Do Not Sell' }, status: 'denied', consent_method: 'api', granted_at: null },
  ],
  organizations: [
    { id: 'org_1', name: 'Acme Corp', domain: 'acme.com', industry: 'Retail', plan: 'pro', is_active: true },
  ],
  user: {
    id: 'user_admin', email: 'demo@consenthub.com', name: 'Demo Admin', role: 'admin'
  }
};

const originalFetch = window.fetch;

window.fetch = async function(resource, config) {
  // Only intercept if we are in demo mode
  if (!localStorage.getItem('ch_demo_mode')) {
    return originalFetch(resource, config);
  }

  console.log("Mocking request:", resource, config);

  const url = new URL(resource, window.location.origin);
  const path = url.pathname;
  const method = config?.method || 'GET';

  const respond = (data, status = 200) => {
    return Promise.resolve({
      ok: status >= 200 && status < 300,
      status: status,
      json: () => Promise.resolve(data)
    });
  };

  // Auth
  if (path.includes('/auth/login') && method === 'POST') {
    return respond({ access_token: 'demo-token', user: MOCK_DATA.user });
  }
  if (path.includes('/auth/me') && method === 'GET') {
    return respond(MOCK_DATA.user);
  }

  // Health
  if (path.includes('/health') && method === 'GET') {
    return respond({ status: 'healthy', version: '1.0.0 (Demo Mode)' });
  }

  // Policies
  if (path.includes('/consents/policies') && method === 'GET') {
    return respond({ items: MOCK_DATA.policies, total: MOCK_DATA.policies.length, page: 1, pages: 1 });
  }
  if (path.includes('/consents/policies') && method === 'POST') {
    const body = JSON.parse(config.body);
    const newPolicy = { id: 'pol_' + Date.now(), ...body, is_active: true };
    MOCK_DATA.policies.push(newPolicy);
    return respond(newPolicy, 201);
  }

  // Records
  if (path.includes('/consents/records') && method === 'GET') {
    return respond({ items: MOCK_DATA.records, total: MOCK_DATA.records.length, page: 1, pages: 1 });
  }
  if (path.includes('/consents/records') && method === 'POST') {
    const body = JSON.parse(config.body);
    const policy = MOCK_DATA.policies.find(p => p.id === body.policy_id);
    const newRecord = {
      id: 'rec_' + Date.now(),
      data_subject_id: body.data_subject_id,
      policy: policy ? { name: policy.name } : { name: 'Unknown' },
      status: body.status,
      consent_method: body.consent_method,
      granted_at: body.status === 'granted' ? new Date().toISOString() : null
    };
    MOCK_DATA.records.push(newRecord);
    return respond(newRecord, 201);
  }
  if (path.match(/\/consents\/records\/rec_.+\/withdraw/) && method === 'PUT') {
    const id = path.split('/')[3];
    const rec = MOCK_DATA.records.find(r => r.id === id);
    if (rec) {
      rec.status = 'withdrawn';
      return respond(rec);
    }
    return respond({error: 'Not found'}, 404);
  }

  // Analytics
  if (path.includes('/analytics/summary') && method === 'GET') {
    return respond({
      total_records: MOCK_DATA.records.length,
      consent_rate_pct: 50.0,
      by_status: {
        granted: MOCK_DATA.records.filter(r => r.status === 'granted').length,
        denied: MOCK_DATA.records.filter(r => r.status === 'denied').length,
        withdrawn: MOCK_DATA.records.filter(r => r.status === 'withdrawn').length,
      },
      by_method: {
        'web-form': MOCK_DATA.records.filter(r => r.consent_method === 'web-form').length,
        'api': MOCK_DATA.records.filter(r => r.consent_method === 'api').length
      }
    });
  }
  if (path.includes('/analytics/trends') && method === 'GET') {
    // Generate dummy trends
    const trends = [];
    for(let i=30; i>=0; i--) {
       const d = new Date();
       d.setDate(d.getDate() - i);
       trends.push({ date: d.toISOString().split('T')[0], granted: Math.floor(Math.random() * 10), denied: Math.floor(Math.random() * 5) });
    }
    return respond({ trends });
  }

  // Organizations
  if (path.includes('/organizations') && method === 'GET') {
    return respond({ items: MOCK_DATA.organizations, total: MOCK_DATA.organizations.length, page: 1, pages: 1 });
  }

  // Fallback for unmocked routes
  console.warn("Unmocked route in demo mode:", path);
  return respond({error: "Not implemented in Demo mode"}, 404);
};
