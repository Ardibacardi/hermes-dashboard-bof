# Hermes Dashboard — Architecture

## Data Flow

```
TrendTrack API
     │
     ▼
┌─────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  ad-miner   │───▶│  KPI Filtering   │───▶│  Transformation  │
│   plugin    │    │  (50K+ reach,    │    │  (creative       │
│             │    │   14d+ running)  │    │   strategist KB) │
└─────────────┘    └──────────────────┘    └────────┬────────┘
                                                     │
                                                     ▼
                                            ┌─────────────────┐
                                            │  Google Sheets   │
                                            │  "BOF Ad Miner   │
                                            │   Results"       │
                                            └─────────────────┘
```

## Cron Schedule

```
┌───────┬───────┬───────┬───────┬───────┬───────┬───────┐
│  Sun  │  Mon  │  Tue  │  Wed  │  Thu  │  Fri  │  Sat  │
│       │ 9 UTC │       │ 9 UTC │       │ 9 UTC │       │
│       │   🔍  │       │   🔍  │       │   🔍  │       │
└───────┴───────┴───────┴───────┴───────┴───────┴───────┘
```

## Tool Architecture (Plugin)

```
plugin.yaml ──▶ declares 5 tools, 1 skill, 1 env var
     │
     ├── schemas.py ──▶ tool definitions (what LLM sees)
     │
     └── tools.py ──▶ handler implementations
          ├── trendtrack_lookup()      — zero-credit ID resolution
          ├── trendtrack_search_ads()  — POST /v1/ads/query
          ├── trendtrack_get_overview()— brandtracker overview
          ├── filter_ads_by_kpi()      — threshold + scoring
          └── transform_for_metabolae()— creative brief scaffold
```

## Future: Dashboard UI

Planned integration points:
- Claude API for creative brief generation
- GitHub API for version-controlled ad copy
- Live TrendTrack data feeds
- KPI monitoring dashboards
