# BOF Ad Miner — Full Project Plan

## Overview

A Hermes Agent system that searches TrendTrack API and Meta Ads Library API for high-performing Bottom-of-Funnel (BOF) ads in the health/supplement space, filters them by KPI thresholds (impressions, reach, spend), and transforms winning ads into Metabolae-branded creatives using the creative strategist knowledge base.

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                    CRON SCHEDULER                     │
│  (daily/weekly triggers with cronjob tool)            │
└────────────────────┬─────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────┐
│              AD-MINER PLUGIN (Phase 2)                │
│                                                      │
│  Tools:                                              │
│  ├─ trendtrack_search_ads(domain, niche, kpis)       │
│  ├─ meta_ads_search(query, countries, date_range)    │
│  ├─ filter_ads_by_kpi(ads, thresholds)               │
│  ├─ get_ad_detail(ad_id, platform)                   │
│  └─ transform_for_brand(ad, brand_context)           │
│                                                      │
│  Bundled: bof-ad-miner SKILL.md                      │
└────────────────────┬─────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────┐
│              BOF-AD-MINER SKILL (Phase 1)             │
│                                                      │
│  Step-by-step workflow:                              │
│  1. Identify target competitors/niches               │
│  2. Resolve via TrendTrack lookup                    │
│  3. Query top ads with KPI filters                   │
│  4. Cross-reference with Meta Ads Library (EU/UK)    │
│  5. Extract hooks, angles, creative patterns         │
│  6. Transform for Metabolae using knowledge base     │
│  7. Output formatted ad briefs                       │
└────────────────────┬─────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────┐
│         CREATIVE STRATEGIST KNOWLEDGE BASE            │
│                                                      │
│  Files: /Users/bigbootylover/workspace/               │
│         creative-strategist/markdown/                 │
│                                                      │
│  Used for:                                           │
│  ├─ Metabolae brand voice/tone/positioning           │
│  ├─ Ceylon Cinnamon market & competitor intel        │
│  ├─ Direct response ad principles (Schwartz, Ogilvy) │
│  ├─ Scientific angles & claims validation            │
│  └─ Ad copy transformation patterns                  │
└──────────────────────────────────────────────────────┘
```

## API Mapping

### TrendTrack API
| Endpoint | Purpose | Credit Cost |
|----------|---------|-------------|
| `GET /v1/lookup?q=...&type=auto` | Resolve competitor domain/brand to IDs | 0 (free) |
| `GET /v1/brandtrackers/{id}/overview` | Brand performance overview | 1 |
| `GET /v1/brandtrackers/{id}/top-ads?sortBy=reach&limit=N` | Top ads by reach | 1 per row |
| `POST /v1/ads/query` | Public ad discovery with filters | 1 per row |
| `GET /v1/ads/{id}` | Single ad detail | 1 |
| `GET /v1/ads?search=keyword&sortBy=reach` | Search ads by keyword | 1 per row |

**Key sortBy fields for performance:**
- `reach` / `impressions` — total reach
- `reachDelta7d`, `reachDelta14d`, `reachDelta30d` — growth signals
- `rankDelta7d`, `rankDelta14d` — rank movement
- `currentRank` — current position

**Auth:** `Authorization: Bearer $TRENDTRACK_API_KEY`
**Base URL:** `https://api.trendtrack.io`

### Meta Ads Library API
| Parameter | Purpose |
|-----------|---------|
| `ad_reached_countries=['GB','FR','DE',...]` | REQUIRED — EU/UK for commercial ads |
| `search_terms='keyword'` | Search ad text |
| `ad_type='ALL'` | All ad types |
| `ad_active_status='ACTIVE'` | Currently running |
| `ad_delivery_date_min/max` | Date range filter |
| `search_page_ids=['page_id']` | Filter by advertiser Page |

**KPI data available (EU/UK ads only):**
- `impressions` — range buckets (e.g., "1000-5000")
- `spend` — range buckets (e.g., "100-499")
- `demographic_distribution` — age/gender/region percentages

**Limitations:**
- No CTR, conversion, or engagement data
- Impressions/spend are RANGES, not exact numbers
- Only EU/UK ads return performance data for commercial ads
- Requires identity verification + Meta Developer app

**Auth:** `access_token=<TOKEN>` via Graph API
**Base URL:** `https://graph.facebook.com/v22.0/ads_archive`

## KPI Thresholds (Configurable)

| Metric | Threshold | Notes |
|--------|-----------|-------|
| Min impressions | 50,000+ | From Meta "50000-100000" bucket or higher |
| Min reach (TrendTrack) | 100,000+ | Sort by `reach` descending |
| Ad running duration | 14+ days | `daysRunning >= 14` |
| Rank movement | `rankDelta7d > 0` | Rising in rank = working |
| Spend range (Meta) | "500-999" bucket or higher | Indicates advertiser commitment |

## Competitor Targets

Based on Metabolae market research:
- **Lirae** (primary — dropshipping competitor, Ceylon Cinnamon)
- General search: "Ceylon cinnamon supplement" ads
- Adjacent: blood sugar, metabolic health, natural supplements
- Category IDs from TrendTrack facets: supplements, health & wellness

## Ad Transformation Pipeline

For each winning ad found:
1. **Extract structure**: hook → problem → solution → proof → CTA
2. **Identify the core angle**: what emotional/physical problem does it solve?
3. **Map to Metabolae**: replace competitor claims with Metabolae's verified advantages
   - Real certifications vs. competitor's fake ones
   - Transparent sourcing vs. hidden supply chains
   - Published COAs vs. no lab results
4. **Apply creative principles** from knowledge base:
   - Schwartz: match the market sophistication level
   - Ogilvy: factual, specific, no fluff
   - Hopkins: scientific advertising with testable claims
5. **Output**: formatted ad brief with hook, body, CTA, and visual direction

## Phase 1 Deliverable: Skill

File: `~/.hermes/skills/software-development/bof-ad-miner/SKILL.md`

What the skill contains:
- Complete workflow instructions for Hermes to follow
- API endpoints, parameters, auth patterns
- KPI filtering rules
- Competitor targets for Metabolae
- Ad transformation methodology
- Reference links to creative strategist knowledge base files

## Phase 2 Deliverable: Plugin

Directory: `~/.hermes/plugins/ad-miner/`
Files:
- `plugin.yaml` — manifest with tool declarations
- `schemas.py` — tool schemas (what the LLM sees)
- `tools.py` — handler implementations (actual API calls)
- `skills/bof-ad-miner/SKILL.md` — bundled skill

## Phase 3: Cron Job

Schedule: `every 48h` or `0 9 * * 1,3,5` (Mon/Wed/Fri at 9am)
Prompt: "Run the bof-ad-miner workflow: search TrendTrack and Meta Ads Library for new high-performing BOF ads in the supplement space, filter by KPI thresholds, and produce transformation briefs for Metabolae."
Delivery: Telegram home channel

## Profile Strategy

| Profile | Role | When |
|---------|------|------|
| `default` | Planning, API research, coordination | Current session |
| `coder` | Plugin/tool building, Python development | Phase 2 |
| `creative-strategist` | Ad analysis, brand transformation | Ad review & transformation steps |

## Environment Variables Needed

```
TRENDTRACK_API_KEY=tt_...          # From app.trendtrack.io/workspace/settings/api
META_ADS_ACCESS_TOKEN=EAAB...      # From Meta Graph API Explorer / Developer app
```

---

*Plan version: 1.0 — Created 2026-06-24*
