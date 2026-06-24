"""
Ad Miner Dashboard — Plugin API module for Hermes Command Center.

Provides backend endpoints for the Ad Miner dashboard tab.
Queries TrendTrack API, reads cron job status, and surfaces
ad mining results, KPI summaries, and transformation pipeline state.
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

# --- Configuration ---
TRENDTRACK_BASE = "https://api.trendtrack.io"
HERMES_HOME = Path(os.getenv("HERMES_HOME", str(Path.home() / ".hermes")))
CRON_OUTPUT_DIR = HERMES_HOME / "cron" / "output"
STATE_FILE = HERMES_HOME / "plugins" / "ad-miner-dashboard" / "state.json"

# --- Helpers ---

def _load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"last_run": None, "total_ads_mined": 0, "credits_remaining": None}


def _save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def _cron_output_files():
    """List recent BOF ad miner output files."""
    if not CRON_OUTPUT_DIR.exists():
        return []
    files = sorted(CRON_OUTPUT_DIR.glob("bof-ad-miner-*.json"), reverse=True)
    return [{"name": f.name, "mtime": datetime.fromtimestamp(f.stat().st_mtime).isoformat(), "size": f.stat().st_size} for f in files[:10]]


# --- Endpoints ---

def get_status():
    """Dashboard status summary — returns state + cron output files."""
    state = _load_state()
    return json.dumps({
        "status": "ok",
        "last_run": state.get("last_run"),
        "total_ads_mined": state.get("total_ads_mined", 0),
        "credits_remaining": state.get("credits_remaining"),
        "recent_outputs": _cron_output_files(),
        "next_cron_run": "Mon/Wed/Fri 09:00 UTC",
    })


def get_recent_results(limit: int = 5):
    """Return data from the most recent mining runs."""
    files = _cron_output_files()
    results = []
    for f in files[:limit]:
        try:
            data = json.loads(f.read_text())
            results.append({
                "file": f["name"],
                "date": f["mtime"],
                "data": data if isinstance(data, dict) else {"raw": str(data)[:500]},
            })
        except Exception:
            results.append({"file": f["name"], "date": f["mtime"], "error": "unreadable"})
    return json.dumps({"results": results})


def check_trendtrack():
    """Check TrendTrack API access and credits."""
    import urllib.request

    key = os.getenv("TRENDTRACK_API_KEY", "")
    if not key:
        return json.dumps({"status": "error", "error": "TRENDTRACK_API_KEY not set"})

    try:
        # Check /v1/me
        req = urllib.request.Request(
            f"{TRENDTRACK_BASE}/v1/me",
            headers={"Authorization": f"Bearer {key}"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            me_data = json.loads(resp.read().decode())

        # Check credits
        req2 = urllib.request.Request(
            f"{TRENDTRACK_BASE}/v1/usage",
            headers={"Authorization": f"Bearer {key}"},
        )
        with urllib.request.urlopen(req2, timeout=10) as resp2:
            credits = resp2.headers.get("x-credits-remaining", "unknown")

        state = _load_state()
        state["credits_remaining"] = credits
        _save_state(state)

        return json.dumps({
            "status": "ok",
            "authenticated": True,
            "workspace": me_data if isinstance(me_data, dict) else {"raw": str(me_data)[:200]},
            "credits_remaining": credits,
        })
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})
