/**
 * Ad Miner Dashboard — Frontend UI
 * 
 * Tab for Hermes Command Center showing BOF ad mining pipeline status,
 * TrendTrack credits, recent ad results, and transformation pipeline state.
 */

(function() {
  const API_BASE = '/api/dashboard/plugins/ad-miner-dashboard';

  // --- State ---
  let state = {
    status: null,
    trendtrack: null,
    recentResults: [],
    loading: true
  };

  // --- API calls ---
  async function fetchAPI(endpoint) {
    try {
      const res = await fetch(`${API_BASE}/${endpoint}`);
      return await res.json();
    } catch (e) {
      return { status: 'error', error: e.message };
    }
  }

  async function refreshAll() {
    state.loading = true;
    render();
    const [status, trendtrack, results] = await Promise.all([
      fetchAPI('status'),
      fetchAPI('check-trendtrack'),
      fetchAPI('recent-results?limit=5')
    ]);
    state.status = status;
    state.trendtrack = trendtrack;
    state.recentResults = (results && results.results) ? results.results : [];
    state.loading = false;
    render();
  }

  // --- Render ---
  function render() {
    const root = document.getElementById('ad-miner-root');
    if (!root) return;

    if (state.loading) {
      root.innerHTML = '<div class="ad-miner-loading">Loading pipeline status...</div>';
      return;
    }

    const credits = state.trendtrack && state.trendtrack.credits_remaining ? state.trendtrack.credits_remaining : '--';
    const lastRun = state.status && state.status.last_run ? new Date(state.status.last_run).toLocaleString() : 'Never';
    const totalAds = state.status ? state.status.total_ads_mined : 0;

    root.innerHTML = `
      <div class="ad-miner-grid">
        <!-- Status Cards -->
        <div class="ad-miner-card">
          <div class="ad-miner-card-header">Credits</div>
          <div class="ad-miner-card-value ${credits === '--' ? 'dim' : ''}">${credits}</div>
          <div class="ad-miner-card-sub">TrendTrack remaining</div>
        </div>
        <div class="ad-miner-card">
          <div class="ad-miner-card-header">Last Run</div>
          <div class="ad-miner-card-value">${lastRun}</div>
          <div class="ad-miner-card-sub">Next: Mon/Wed/Fri 09:00 UTC</div>
        </div>
        <div class="ad-miner-card">
          <div class="ad-miner-card-header">Ads Mined</div>
          <div class="ad-miner-card-value">${totalAds.toLocaleString()}</div>
          <div class="ad-miner-card-sub">Total pipeline output</div>
        </div>

        <!-- Recent Results -->
        <div class="ad-miner-section">
          <h3>Recent Mining Runs</h3>
          ${state.recentResults.length === 0
            ? '<div class="ad-miner-empty">No results yet. First run scheduled for Friday.</div>'
            : state.recentResults.map(r => `
              <div class="ad-miner-result-row">
                <span class="ad-miner-result-date">${new Date(r.date).toLocaleDateString()}</span>
                <span class="ad-miner-result-file">${r.file}</span>
                ${r.error ? `<span class="ad-miner-result-error">${r.error}</span>` : ''}
              </div>
            `).join('')
          }
        </div>
      </div>
    `;
  }

  // --- Init ---
  function init() {
    // Create root element if not provided by dashboard
    let root = document.getElementById('ad-miner-root');
    if (!root) {
      root = document.createElement('div');
      root.id = 'ad-miner-root';
      document.querySelector('.dashboard-content')?.appendChild(root);
    }
    refreshAll();
    // Auto-refresh every 60s
    setInterval(refreshAll, 60000);
  }

  // Wait for DOM
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
