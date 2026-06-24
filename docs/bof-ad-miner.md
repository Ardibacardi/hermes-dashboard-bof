---
name: bof-ad-miner
description: "Search TrendTrack and Meta Ads Library APIs for high-performing Bottom-of-Funnel ads in the supplement space, filter by KPIs, and transform winning ads into Metabolae-branded creatives using the creative strategist knowledge base."
version: 1.0.0
author: Arthur Moonen
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [advertising, ecommerce, metabolae, trendtrack, meta-ads, creative-strategy]
---

# BOF Ad Miner

Search TrendTrack and Meta Ads Library APIs for high-performing Bottom-of-Funnel (BOF) ads in the health/supplement niche, filter by KPI thresholds, and transform winning ads for Metabolae.

## When to Use

- User asks to find competitor ads, winning creatives, or ad inspiration
- User wants to research what's working in supplements/metabolic health space
- User asks to "mine ads" or "spy on competitor ads"
- User wants ad transformation briefs for Metabolae
- Cron job fires for scheduled ad mining

## Prerequisites

### Environment Variables

```bash
TRENDTRACK_API_KEY=***          # From https://app.trendtrack.io/workspace/settings/api
META_ADS_ACCESS_TOKEN=***      # From Meta Graph API Explorer via Meta Developer app
```

### Skills to Load

Load these alongside this skill:
- `creative-strategist-knowledge` — for brand voice, market intel, ad principles

### Knowledge Base Location

```
/Users/bigbootylover/workspace/creative-strategist/markdown/
```

Key files for ad transformation:
- `breakthrough advertising by eugene m.md` — Schwartz's market sophistication levels
- `Ogilvy on Advertising PDF.md` — factual, specific ad principles
- `sceintific advertising.md` — Hopkins' testable claims framework
- `Metabolae Marketing Agency Project Brief.md` — competitor intel, buyer persona
- `pdp metabolae.md` — product detail page content
- `New scientific angles for Ceylon Cinnamon 7200mg direct response advertising.md` — ad angles
- `METABOLAE bloodpressure mechanism explanation new.md` — product mechanism
- `Great Leads PDF.md` — lead generation patterns

---

## Workflow

### Phase 1: Competitor & Niche Identification

**Metabolae default competitors (from market research):**

| Competitor | Domain | Why target |
|------------|--------|------------|
| Lirae | (dropshipper — search by name) | Primary Ceylon Cinnamon competitor, fake trust signals |
| General | Search: "ceylon cinnamon supplement" | Market-wide BOF ad discovery |

**Broader niche targets:**
- Search terms: "blood sugar support", "cinnamon supplement", "metabolic health", "natural insulin support"
- TrendTrack category: supplements, health & wellness (resolve via facets)

### Phase 2: TrendTrack API Search

**Step 2.1 — Validate access:**

```bash
curl -s "https://api.trendtrack.io/v1/me" \
  -H "Authorization: Bearer $TRENDTRACK_API_KEY"

curl -s "https://api.trendtrack.io/v1/usage" \
  -H "Authorization: Bearer $TRENDTRACK_API_KEY"
```

Always check `x-credits-remaining` header before heavy calls.

**Step 2.2 — Resolve competitor identifier (zero-credit):**

```bash
curl -s "https://api.trendtrack.io/v1/lookup?q=COMPETITOR_DOMAIN&type=auto" \
  -H "Authorization: Bearer $TRENDTRACK_API_KEY"
```

If lookup returns a `brandtracker` → use `brandtracker.id` for deep dive.
If only `shop` or `advertiser` → use those IDs for ad queries.

**Step 2.3 — Get competitor overview (if brandtracker):**

```bash
curl -s "https://api.trendtrack.io/v1/brandtrackers/BRANDTRACKER_ID/overview" \
  -H "Authorization: Bearer $TRENDTRACK_API_KEY"
```

Review: total ads, spend range, traffic, creative format mix, top hooks, landing page breakdown.

**Step 2.4 — Extract top-performing ads:**

```bash
# Sort by reach (highest impressions first)
curl -s "https://api.trendtrack.io/v1/brandtrackers/BRANDTRACKER_ID/top-ads?sortBy=reach&limit=25" \
  -H "Authorization: Bearer $TRENDTRACK_API_KEY"

# Sort by rank movers (rising stars — most actionable)
curl -s "https://api.trendtrack.io/v1/brandtrackers/BRANDTRACKER_ID/top-ads?sortBy=rankDelta7d&limit=25" \
  -H "Authorization: Bearer $TRENDTRACK_API_KEY"
```

**Step 2.5 — Public ad discovery (broad search):**

```json
POST /v1/ads/query
{
  "search": "ceylon cinnamon supplement",
  "sortBy": "reach",
  "order": "desc",
  "limit": 25,
  "mediaType": ["video", "image"],
  "platforms": ["facebook", "instagram"]
}
```

**Key sortBy values for BOF performance signals:**

| sortBy | What it means | Use when |
|--------|---------------|----------|
| `reach` | Total estimated reach | Finding biggest spenders |
| `reachDelta7d` | Reach growth in 7 days | Finding scaling ads |
| `reachDelta14d` | Reach growth in 14 days | Confirming sustained scaling |
| `rankDelta7d` | Rank movement in 7 days | Finding rising stars |
| `currentRank` | Current rank position | Current top performers |
| `daysRunning` | How long ad has been live | Filtering for proven ads |
| `impressions` | Alias for reach | Same as reach |

### Phase 3: Meta Ads Library API (EU/UK Data)

**Use for:** Getting impression/spend ranges and demographic data on ads delivered to EU/UK.

**Step 3.1 — Search by competitor page ID or keywords:**

```bash
curl -G "https://graph.facebook.com/v22.0/ads_archive" \
  -d "search_terms='ceylon cinnamon'" \
  -d "ad_type=ALL" \
  -d "ad_reached_countries=['GB','FR','DE','NL','IT','ES']" \
  -d "ad_active_status=ACTIVE" \
  -d "ad_delivery_date_min=2026-01-01" \
  -d "fields=ad_creative_bodies,page_name,page_id,impressions,spend,demographic_distribution,ad_delivery_start_time,publisher_platforms,ad_snapshot_url" \
  -d "limit=25" \
  -d "access_token=$META_ADS_ACCESS_TOKEN"
```

**Step 3.2 — If you have a specific competitor's page_id:**

Add `search_page_ids=['PAGE_ID']` to the query.

**What you get from Meta that TrendTrack doesn't provide:**
- `impressions` — range buckets: "0-1000", "1000-5000", "5000-10000", "10000-50000", "50000-100000", "100000-200000", "200000-500000", "500000-1000000", "1000000+"
- `spend` — range buckets: "0-99", "100-499", "500-999", "1000-5000", "5000-10000", "10000-50000", "50000-100000", "100000+"
- `demographic_distribution` — age/gender/region percentage breakdowns
- `ad_creative_bodies` — actual ad copy text
- `ad_snapshot_url` — link to view the creative

### Phase 4: KPI Filtering

Apply these thresholds to filter for truly high-performing BOF ads:

#### Hard Thresholds (must meet ALL)

| Metric | Minimum | Source |
|--------|---------|--------|
| Impressions/Reach | ≥ 50,000 | Meta: "50000-100000" bucket or higher; TrendTrack: reach ≥ 50000 |
| Days running | ≥ 14 days | TrendTrack: `daysRunning >= 14`; Meta: `ad_delivery_start_time` ≥ 14 days ago |
| Ad active status | ACTIVE | Both APIs |

#### Soft Signals (rank ads by these)

| Signal | Weight | Meaning |
|--------|--------|---------|
| rankDelta7d > 0 | High | Rising in rank = audience responding |
| reachDelta7d > 0 | High | Advertiser is scaling spend |
| Spend ≥ "500-999" bucket | Medium | Advertiser commitment |
| Multiple platform delivery | Low | Cross-platform = broader testing |
| Long running time (30+ days) | Medium | Sustained performance |

#### Filtering Logic (Python pseudocode):

```python
def passes_kpi_threshold(ad, platform):
    """Returns True if ad meets minimum KPI thresholds."""
    if platform == "meta":
        # Parse impression range
        imp_bucket = ad.get("impressions", "0-1000")
        min_imp = parse_impression_lower_bound(imp_bucket)
        if min_imp < 50000:
            return False

        # Check spend range
        spend_bucket = ad.get("spend", "0-99")
        min_spend = parse_spend_lower_bound(spend_bucket)
        if min_spend < 500:
            return False

    elif platform == "trendtrack":
        if ad.get("reach", 0) < 50000:
            return False

    # Running duration check
    if ad.get("daysRunning", 0) < 14:
        return False

    return True

def score_ad(ad, platform):
    """Score ad by performance signals (higher = better)."""
    score = 0
    if platform == "trendtrack":
        if ad.get("rankDelta7d", 0) > 0: score += 3
        if ad.get("reachDelta7d", 0) > 0: score += 3
        if ad.get("daysRunning", 0) >= 30: score += 2
        if ad.get("rankDelta30d", 0) > 0: score += 2
    elif platform == "meta":
        imp_lower = parse_impression_lower_bound(ad.get("impressions", ""))
        if imp_lower >= 100000: score += 3
        elif imp_lower >= 50000: score += 1
        spend_lower = parse_spend_lower_bound(ad.get("spend", ""))
        if spend_lower >= 1000: score += 3
        elif spend_lower >= 500: score += 1
    return score
```

### Phase 5: Ad Creative Extraction

For each ad that passes KPI filters, extract:

1. **Hook** — First 1-2 sentences or first 3 seconds (for video)
2. **Core angle** — What problem does it solve? What desire does it trigger?
3. **Body/middle** — Key claims, features, social proof
4. **CTA** — Call to action phrasing
5. **Creative format** — Video, image, carousel; aspect ratio; text overlay style
6. **Landing page type** — Home, product, collection, or dedicated landing page
7. **Platform** — Facebook, Instagram, or both

From TrendTrack brandtracker overview, also capture:
- Creative format mix (video vs image %)
- Top-performing hooks (verbatim)
- Best landing pages
- Testing timeline

### Phase 6: Metabolae Brand Transformation

**Use the creative strategist knowledge base for this phase.**

#### Step 6.1 — Load relevant knowledge base files

Always read these before transforming:
- `Metabolae Marketing Agency Project Brief.md` — buyer persona, competitor intel, objection handling
- `pdp metabolae.md` — product details, claims, pricing
- `New scientific angles for Ceylon Cinnamon 7200mg direct response advertising.md` — proven angles
- `breakthrough advertising by eugene m.md` — market sophistication framework

#### Step 6.2 — Determine market sophistication level (Schwartz framework)

For Ceylon Cinnamon supplements, the market is at **Level 3-4** (out of 5):
- Consumers know the basic claim (cinnamon helps blood sugar)
- They've seen competitors and are becoming skeptical
- They need differentiation: "Why Metabolae vs the rest?"
- Focus on mechanism, transparency, verification

#### Step 6.3 — Transformation mapping

For each winning competitor ad, map:

| Competitor Element | Metabolae Transformation |
|-------------------|-------------------------|
| Vague "third-party tested" | "Published COAs available — scan QR on bottle" |
| "Rated 4.8 Excellent" (no source) | Real review platform integration |
| "Doctor recommended" (unnamed) | Specific certifications (GMP, etc.) |
| Generic "Ceylon from Sri Lanka" | "Single-origin Sri Lankan, batch-traceable" |
| "No fillers" (empty claim) | "Ingredients list: 2 items. That's it." |
| Dropshipper trust signals | "Family-operated. We answer emails personally." |
| Perpetual sale pricing | Value-based pricing with bundle savings |
| BOF urgency ("low stock") | Informational urgency ("FDA recalled 16+ brands") |

#### Step 6.4 — Output format: Ad Transformation Brief

For each winning ad found, produce:

```markdown
## Ad Transformation Brief #[N]

### Source Ad
- **Platform:** [Meta/Instagram/Both]
- **Advertiser:** [Name]
- **Format:** [Video/Image/Carousel]
- **Impressions:** [range]
- **Running since:** [date]
- **Ad snapshot:** [URL]

### Original Hook
> [Verbatim hook text]

### Original Angle
[What problem/desire does it target?]

### Original CTA
> [Verbatim CTA]

### Metabolae Transformation
**New Hook:**
> [Transformed hook — same emotional trigger, Metabolae's advantage]

**New Angle:**
[How Metabolae solves it better — transparency angle, certification angle, etc.]

**Key Claims to Use:**
- [Claim 1 with evidence from knowledge base]
- [Claim 2 with evidence from knowledge base]

**New CTA:**
> [Transformed CTA with Metabolae-specific offer]

**Visual Direction:**
[Format, aspect ratio, text overlay style, key visual elements]

**Landing Page:** [Which Metabolae page this should point to]

### Why This Works (Schwartz Level)
[Brief analysis of market sophistication and why this approach fits]
```

---

## Edge Cases & Pitfalls

### TrendTrack API

1. **Credit exhaustion** — Always check `x-credits-remaining` before bulk calls. Start with low `limit` values and increase only if needed.
2. **Lookup returns nothing** — The competitor might not be indexed. Fall back to `POST /v1/ads/query` with keyword search.
3. **Brandtracker not found** — Not all competitors are tracked. Use advertiser or shop endpoints instead.
4. **Deprecated parameters** — Do NOT use `period` or `snapshotDate` on current top-ads ranking calls.
5. **Name/domain in shop queries** — Only use `search` and `searchType` in `POST /v1/shops/query`; never send `name` or `domain`.

### Meta Ads Library API

1. **No EU/UK delivery** — Ads that only ran in US won't have impression/spend data. These are still useful for creative analysis but can't be KPI-filtered.
2. **Range buckets only** — "50000-100000" is the best you get. Can't distinguish 51K from 99K.
3. **Rate limiting** — Meta aggressively rate-limits. Use small `limit` values (10-25) and add delays between pages.
4. **Access token expiry** — User tokens expire. Long-lived tokens need a Meta app in production mode.
5. **No creative download** — `ad_snapshot_url` lets you VIEW the ad in a browser, not download media files.
6. **Search terms are fuzzy** — "ceylon cinnamon" also matches "cinnamon ceylon" and partial matches.

---

## Complete Script: BOF Ad Mining Run

This is the end-to-end sequence for a full mining run:

```
1. Load skill: creative-strategist-knowledge
2. Validate: curl /v1/me + /v1/usage (TrendTrack) — log credit balance
3. For each competitor target:
   a. TrendTrack lookup → get brandtracker/advertiser/shop ID
   b. If brandtracker: get overview, then top-ads by reach and rankDelta7d
   c. If advertiser: query ads with filters
4. Broader discovery: POST /v1/ads/query with category/niche keywords
5. For each ad from TrendTrack: add to candidate pool
6. Meta Ads Library: search for same competitors/keywords in EU/UK
7. For each Meta ad: add to candidate pool (with impression/spend ranges)
8. Filter combined pool through KPI thresholds
9. Score and rank surviving ads
10. For top N ads (default: 10):
    a. Extract hook, angle, CTA, format
    b. Load Metabolae brand files from knowledge base
    c. Produce transformation brief
11. Output: full report with top briefs
```

---

## Reference: Impression/Spend Bucket Parsing

```python
def parse_impression_lower_bound(bucket: str) -> int:
    """Parse Meta impression range string to lower bound integer."""
    mapping = {
        "0-1000": 0, "1000-5000": 1000, "5000-10000": 5000,
        "10000-50000": 10000, "50000-100000": 50000,
        "100000-200000": 100000, "200000-500000": 200000,
        "500000-1000000": 500000, "1000000+": 1000000,
    }
    return mapping.get(bucket.strip(), 0)

def parse_spend_lower_bound(bucket: str) -> int:
    """Parse Meta spend range string to lower bound integer."""
    mapping = {
        "0-99": 0, "100-499": 100, "500-999": 500,
        "1000-5000": 1000, "5000-10000": 5000,
        "10000-50000": 10000, "50000-100000": 50000,
        "100000+": 100000,
    }
    return mapping.get(bucket.strip(), 0)
```
