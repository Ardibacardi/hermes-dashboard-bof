"""
Backend routes for the Ad Miner dashboard plugin.

Updated to read markdown output files (actual cron output format).
"""
from __future__ import annotations

import json
import os
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter

router = APIRouter()
TRENDTRACK_BASE = "https://api.trendtrack.io"

def _hermes_home() -> Path:
    try:
        from hermes_cli.config import get_hermes_home
        return Path(get_hermes_home()).expanduser()
    except Exception:
        return Path(os.environ.get("HERMES_HOME", "~/.hermes")).expanduser()

def _load_state() -> Dict[str, Any]:
    state_file = _hermes_home() / "plugins" / "ad-miner-dashboard" / "state.json"
    if state_file.exists():
        try: return json.loads(state_file.read_text())
        except: pass
    return {"last_run": None, "total_ads_mined": 0, "credits_remaining": None}

def _save_state(state: Dict[str, Any]) -> None:
    f = _hermes_home() / "plugins" / "ad-miner-dashboard" / "state.json"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(state, indent=2))

def _scan_outputs() -> List[Dict[str, Any]]:
    """Scan cron output directories for BOF ad miner results."""
    results = []
    output_root = _hermes_home() / "cron" / "output"

    # Check job-specific folders for .md files
    for job_dir in output_root.iterdir():
        if not job_dir.is_dir(): continue
        for md_file in sorted(job_dir.glob("*.md"), reverse=True):
            try:
                text = md_file.read_text()
                # Extract key metrics from the markdown
                credits = re.search(r'([\d,]+)\s*credits?\s*remaining', text)
                briefs = len(re.findall(r'### Brief #\d', text))
                ads_scanned = re.search(r'(\d+)\s*ads?\s*scanned', text)
                if briefs > 0 or (credits and ads_scanned):
                    results.append({
                        "file": str(md_file.relative_to(output_root)),
                        "date": datetime.fromtimestamp(md_file.stat().st_mtime, tz=timezone.utc).isoformat(),
                        "size": md_file.stat().st_size,
                        "briefs": briefs,
                        "ads_scanned": ads_scanned.group(1) if ads_scanned else None,
                        "credits_remaining": credits.group(1) if credits else None,
                    })
            except: pass
    return results[:10]

@router.get("/status")
async def status() -> Dict[str, Any]:
    state = _load_state()
    outputs = _scan_outputs()
    # Update state from latest output
    if outputs:
        latest = outputs[0]
        state["last_run"] = latest["date"]
        state["total_ads_mined"] = latest.get("briefs", 0)
        if latest.get("credits_remaining"):
            state["credits_remaining"] = latest["credits_remaining"]
        _save_state(state)
    return {
        "ok": True,
        "last_run": state.get("last_run"),
        "total_ads_mined": state.get("total_ads_mined", 0),
        "credits_remaining": state.get("credits_remaining"),
        "recent_outputs": outputs,
        "next_cron_run": "Mon/Wed/Fri 09:00 UTC",
    }

@router.get("/recent-results")
async def recent_results(limit: int = 5) -> Dict[str, Any]:
    return {"ok": True, "results": _scan_outputs()[:limit]}

@router.get("/check-trendtrack")
async def check_trendtrack() -> Dict[str, Any]:
    key = os.getenv("TRENDTRACK_API_KEY", "")
    if not key: return {"ok": False, "error": "TRENDTRACK_API_KEY not set"}
    try:
        req = urllib.request.Request(f"{TRENDTRACK_BASE}/v1/me", headers={"Authorization": f"Bearer {key}"})
        with urllib.request.urlopen(req, timeout=10) as r: me = json.loads(r.read().decode())
        req2 = urllib.request.Request(f"{TRENDTRACK_BASE}/v1/usage", headers={"Authorization": f"Bearer {key}"})
        with urllib.request.urlopen(req2, timeout=10) as r2: credits = r2.headers.get("x-credits-remaining", "?")
        state = _load_state(); state["credits_remaining"] = credits; _save_state(state)
        return {"ok": True, "authenticated": True, "workspace": me if isinstance(me,dict) else {"raw":str(me)[:200]}, "credits_remaining": credits}
    except Exception as e:
        return {"ok": False, "error": str(e)}
