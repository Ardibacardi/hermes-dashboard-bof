/**
 * Ad Miner Dashboard — Hermes plugin entry point
 * 
 * Uses __HERMES_PLUGIN_SDK__ for React, API calls, and theme tokens.
 * register() returns the tab component for Hermes to mount.
 */

(function() {
  var SDK = window.__HERMES_PLUGIN_SDK__;
  if (!SDK || !SDK.React) {
    console.error("Ad Miner: Hermes Plugin SDK not found");
    return;
  }

  var React = SDK.React;
  var h = React.createElement;
  var useState = React.useState;
  var useEffect = React.useEffect;
  var useCallback = React.useCallback;
  var fetchJSON = SDK.fetchJSON;

  // --- API helpers ---

  function safeFetch(endpoint) {
    if (!fetchJSON) {
      return Promise.resolve({ ok: false, error: "SDK.fetchJSON unavailable" });
    }
    return fetchJSON("/api/plugins/ad-miner-dashboard/" + endpoint)
      .then(function(d) { return { ok: true, data: d }; })
      .catch(function(e) { return { ok: false, error: e && e.message ? e.message : String(e) }; });
  }

  // --- Components ---

  function KPICard(props) {
    return h("div", { className: "adm-card" },
      h("div", { className: "adm-card-label" }, props.label),
      h("div", { className: "adm-card-value", style: { color: props.color || "var(--color-accent)" } }, props.value),
      props.sub ? h("div", { className: "adm-card-sub" }, props.sub) : null
    );
  }

  function RecentRuns(props) {
    var results = props.results || [];
    if (!results.length) {
      return h("div", { className: "adm-empty" }, "No mining runs yet. First run Friday 09:00 UTC.");
    }
    return h("div", { className: "adm-section" },
      h("h3", null, "Recent Mining Runs"),
      results.map(function(r, i) {
        return h("div", { key: i, className: "adm-row" },
          h("span", { className: "adm-row-date" }, new Date(r.date).toLocaleDateString()),
          h("span", { className: "adm-row-file" }, r.file),
          r.error ? h("span", { className: "adm-row-err" }, r.error) : null
        );
      })
    );
  }

  // --- Main Page ---

  function AdMinerPage() {
    var creditsState = useState(null);
    var statusState = useState(null);
    var resultsState = useState([]);
    var loadingState = useState(true);
    var credits = creditsState[0], setCredits = creditsState[1];
    var status = statusState[0], setStatus = statusState[1];
    var results = resultsState[0], setResults = resultsState[1];
    var loading = loadingState[0], setLoading = loadingState[1];

    var load = useCallback(function() {
      setLoading(true);
      Promise.all([
        safeFetch("status"),
        safeFetch("check-trendtrack"),
        safeFetch("recent-results?limit=5")
      ]).then(function(packets) {
        if (packets[0].ok) setStatus(packets[0].data);
        if (packets[1].ok) setCredits(packets[1].data);
        if (packets[2].ok && packets[2].data && packets[2].data.results) {
          setResults(packets[2].data.results);
        }
      }).catch(function() {}).finally(function() { setLoading(false); });
    }, []);

    useEffect(function() {
      load();
      var interval = setInterval(load, 60000);
      return function() { clearInterval(interval); };
    }, [load]);

    if (loading) {
      return h("div", { className: "adm-loading" }, "Loading pipeline status...");
    }

    var credsRemaining = credits && credits.credits_remaining ? credits.credits_remaining : "--";
    var lastRun = status && status.last_run ? new Date(status.last_run).toLocaleString() : "Never";
    var totalAds = status ? (status.total_ads_mined || 0) : 0;

    return h("div", { className: "adm-grid" },
      h(KPICard, { label: "TrendTrack Credits", value: credsRemaining, color: credsRemaining === "--" ? "var(--color-muted-foreground)" : "var(--color-accent)", sub: "Remaining" }),
      h(KPICard, { label: "Last Run", value: lastRun, sub: "Next: Mon/Wed/Fri 09:00 UTC" }),
      h(KPICard, { label: "Ads Mined", value: totalAds.toLocaleString(), sub: "Total pipeline output" }),
      h(RecentRuns, { results: results })
    );
  }

  // --- Register with Hermes ---
  // Hermes calls register(SDK) and expects { name, icon, path, component }
  // or the tab is derived from manifest.json

  function register(pluginSDK) {
    return {
      component: function() { return pluginSDK.React.createElement(AdMinerPage); }
    };
  }

  window.__hermes_plugin_register__ = register;
})();
