# Hermes Dashboard — Architecture

## Overview

A Hermes Agent dashboard plugin for Metabolae ad mining operations.
Follows the same plugin pattern as [hermes-chronos-forge](https://github.com/joeynyc/hermes-chronos-forge).

## Data Flow

```
TrendTrack API                    Hermes Cron (0ff6dc052b72)
     │                                    │
     │  /v1/lookup, /v1/ads/query         │  Mon/Wed/Fri 09:00 UTC
     │  /v1/brandtrackers/{id}/top-ads    │  bof-ad-miner skill
     ▼                                    ▼
┌─────────────────┐              ┌──────────────────┐
│  ad-miner       │              │  KPI Filtering   │
│  plugin tools   │──────────────▶  (5 tools)       │
│  (5 tools)      │              │  50K+ reach      │
└─────────────────┘              │  14d+ running    │
                                 └────────┬─────────┘
                                          │
                                          ▼
                                 ┌──────────────────┐
                                 │  Google Sheets    │
                                 │  "BOF Ad Miner    │
                                 │   Results"        │
                                 └────────┬─────────┘
                                          │
                                          ▼
                                 ┌──────────────────┐
                                 │  Dashboard Tab    │
                                 │  /ad-miner        │
                                 │  (this repo)      │
                                 └──────────────────┘
```

## Plugin Architecture

```
plugins/ad-miner-dashboard/dashboard/
├── manifest.json       ┌─ Tab registration: label, icon, path
│                       └─ API module: plugin_api.py
├── plugin_api.py       ┌─ GET /status         → credits, last run, total ads
│                       ├─ GET /recent-results  → last 5 mining runs
│                       └─ GET /check-trendtrack→ API health + credit balance
└── dist/
    ├── index.js        ┌─ Fetches all 3 endpoints on load
    │                   └─ Auto-refreshes every 60s
    └── style.css       └─ Theme-agnostic (uses --color-* tokens)
```

## Hermes Integration Points

| Component | Hermes Path | Purpose |
|-----------|-------------|---------|
| Dashboard tab | `localhost:9119/ad-miner` | Live ops board |
| Plugin files | `~/.hermes/plugins/ad-miner-dashboard/` | Served by Hermes dashboard |
| Cron job | `0ff6dc052b72` | Scheduled ad mining |
| Skill | `bof-ad-miner` | Workflow instructions + tools |
| Tool schemas | `bof-ad-miner/references/schemas.py` | 5 tool definitions |
| Tool handlers | `bof-ad-miner/references/tools.py` | 5 handler implementations |

## Theme

`themes/metabolae-ops.yaml` — dark green + warm amber accent, theme-agnostic plugin UI.
The plugin reads `--color-*` CSS tokens so it works with any Hermes theme.
