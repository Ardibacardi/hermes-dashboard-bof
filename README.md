# Hermes Dashboard

Hermes Agent dashboard for Metabolae e-commerce operations — ad mining, creative strategy, API integrations, and cross-profile workflow orchestration.

## Components

### 🔍 Ad Miner (`ad-miner/`)
BOF ad mining pipeline using TrendTrack API:
- Search for high-performing competitor ads in supplement/health niches
- KPI filtering (50K+ reach, 14+ days running, rank/reach deltas)
- Creative transformation for Metabolae brand using creative strategist knowledge base
- Google Sheets integration for results delivery
- Cron-scheduled via Hermes (Mon/Wed/Fri 9am UTC)

**Plugin files:** `~/.hermes/plugins/ad-miner/`
**Skill:** `bof-ad-miner` (installed in Hermes)

### 📊 Dashboard (`dashboard/`)
Planned: AI dashboard connecting:
- Claude API / Claude-like project workspaces
- GitHub API
- TrendTrack API
- Meta Ads Library API (future)
- Developer workflow metrics

### 🛠 Scripts (`scripts/`)
Utility scripts for data processing, API testing, and automation.

### 📚 Docs (`docs/`)
- Architecture documentation
- API references
- Setup guides

## Setup

### Prerequisites
1. Hermes Agent installed
2. TrendTrack API key (`TRENDTRACK_API_KEY` in `~/.hermes/.env`)
3. Google OAuth configured (for Sheets delivery)
4. Creative strategist knowledge base at `~/workspace/creative-strategist/markdown/`

### Quick Start
```bash
# Load the skill
hermes -s bof-ad-miner

# Run ad mining manually
hermes chat -q "Run the BOF Ad Miner workflow"
```

### Cron Job
```
Job ID: 0ff6dc052b72
Schedule: Mon/Wed/Fri 9am UTC
Skills: bof-ad-miner, creative-strategist-knowledge, google-workspace
Delivery: Google Sheets (fallback: local file)
```

## Profile Architecture

| Profile | Role |
|---------|------|
| `default` | Planning, API research, coordination |
| `coder` | Plugin/tool building, Python development |
| `creative-strategist` | Ad analysis, brand transformation |

## Environment Variables

```bash
TRENDTRACK_API_KEY=***    # From app.trendtrack.io/workspace/settings/api
```

## Related Documentation

- [BOF Ad Miner Skill](./docs/bof-ad-miner.md)
- [Plan Document](./docs/PLAN.md)
- [TrendTrack API Reference](https://docs.trendtrack.io/en/docs)
- [Hermes Agent Plugin Guide](https://hermes-agent.nousresearch.com/docs/guides/build-a-hermes-plugin)
