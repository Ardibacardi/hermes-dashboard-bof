"""
Backend routes for the Ad Miner dashboard plugin.

Uses FastAPI APIRouter — Hermes auto-loads this from the manifest's api_modules.
"""
from __future__ import annotations

import json
import os
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
        try:
            return json.loads(state_file.read_text())
        except Exception:
            pass
    return {"last_run": None, "total_ads_mined": 0, "credits_remaining": None}


def _save_state(state: Dict[str, Any]) -> None:
    state_file = _hermes_home() / "plugins" / "ad-miner-dashboard" / "state.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(state, indent=2))


def _cron_output_files() -> List[Dict[str, Any]]:
    output_dir = _hermes_home() / "cron" / "output"
    if not output_dir.exists():
        return []
    files = sorted(output_dir.glob("bof-ad-miner-*.json"), reverse=True)
    return [
        {
            "name": f.name,
            "date": datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc).isoformat(),
            "size": f.stat().st_size,
        }
        for f in files[:10]
    ]


def _read_latest_results(limit: int = 5) -> List[Dict[str, Any]]:
    files = _cron_output_files()
    results = []
    for f_info in files[:limit]:
        path = _hermes_home() / "cron" / "output" / f_info["name"]
        try:
            data = json.loads(path.read_text())
            results.append({
                "file": f_info["name"],
                "date": f_info["date"],
                "data": data if isinstance(data, dict) else {"raw": str(data)[:500]},
            })
        except Exception:
            results.append({"file": f_info["name"], "date": f_info["date"], "error": "unreadable"})
    return results


@router.get("/status")
async def status() -> Dict[str, Any]:
    state = _load_state()
    return {
        "ok": True,
        "last_run": state.get("last_run"),
        "total_ads_mined": state.get("total_ads_mined", 0),
        "credits_remaining": state.get("credits_remaining"),
        "recent_outputs": _cron_output_files(),
        "next_cron_run": "Mon/Wed/Fri 09:00 UTC",
    }


@router.get("/recent-results")
async def recent_results(limit: int = 5) -> Dict[str, Any]:
    return {
        "ok": True,
        "results": _read_latest_results(limit),
    }


@router.get("/check-trendtrack")
async def check_trendtrack() -> Dict[str, Any]:
    key = os.getenv("TRENDTRACK_API_KEY", "")
    if not key:
        return {"ok": False, "error": "TRENDTRACK_API_KEY not set"}

    try:
        req = urllib.request.Request(
            f"{TRENDTRACK_BASE}/v1/me",
            headers={"Authorization": f"Bearer {key}", "Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            me_data = json.loads(resp.read().decode())

        req2 = urllib.request.Request(
            f"{TRENDTRACK_BASE}/v1/usage",
            headers={"Authorization": f"Bearer {key}"},
        )
        with urllib.request.urlopen(req2, timeout=10) as resp2:
            credits = resp2.headers.get("x-credits-remaining", "unknown")

        state = _load_state()
        state["credits_remaining"] = credits
        _save_state(state)

        return {
            "ok": True,
            "authenticated": True,
            "workspace": me_data if isinstance(me_data, dict) else {"raw": str(me_data)[:200]},
            "credits_remaining": credits,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}
