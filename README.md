# Hermes Dashboard — Ad Miner Plugin

Hermes Agent dashboard extension for Metabolae BOF ad mining operations. A live ops board showing TrendTrack ad intelligence, KPI filtering pipeline, and creative transformation status.

Built as a Hermes dashboard plugin — drop-in install, no fork required.

## What It Provides

- **Ad Miner tab** — live dashboard tab at `/ad-miner` on the Hermes dashboard
- **Credits gauge** — TrendTrack credit balance, refreshed every 60s
- **Pipeline status** — last run time, total ads mined, next cron trigger
- **Recent results** — last 5 mining runs with file links
- **Plugin API** — Python backend endpoints for status, trendtrack check, and results

## Install

```bash
bash install.sh
```

Copies files to:
- `~/.hermes/plugins/ad-miner-dashboard/dashboard/` (plugin)
- `~/.hermes/dashboard-themes/metabolae-ops.yaml` (optional theme)

Then start the dashboard:

```bash
hermes dashboard
```

Open `http://127.0.0.1:9119` and select the **Ad Miner** tab.

If already running, trigger a rescan:

```bash
curl -X POST http://127.0.0.1:9119/api/dashboard/plugins/rescan
```

## File Structure

```
plugins/ad-miner-dashboard/dashboard/
├── manifest.json       # Plugin metadata + tab registration
├── plugin_api.py       # Backend API (status, trendtrack, results)
└── dist/
    ├── index.js        # Frontend UI (credit gauge, pipeline status, recent runs)
    └── style.css       # Theme-agnostic styles using --color-* tokens

themes/
└── metabolae-ops.yaml  # Optional theme (dark green + amber accent)

install.sh              # Drop-in installer
```

## Requirements

- Hermes Agent >= 0.11.0
- TrendTrack API key in `TRENDTRACK_API_KEY` env var
- `bof-ad-miner` skill installed (for cron pipeline)
- `google-workspace` skill for Sheets delivery (optional)

## Related

- [BOF Ad Miner Skill](https://github.com/NousResearch/hermes-agent) — the cron pipeline
- [Hermes Agent Dashboard Docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/dashboard)
- [Chronos Forge](https://github.com/joeynyc/hermes-chronos-forge) — reference implementation
