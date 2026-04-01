# logger.py
# Fix 5: Logging & Observability
#
# Tracks: analysis runs, hallucination flags, provider performance,
# error rates, model drift over time.
# Zero external dependencies — pure Python, writes to local JSONL file.

import json
import os
import time
from datetime import datetime
from pathlib import Path

LOG_FILE = Path("logs/transcript_ai.jsonl")


def _ensure_log_dir():
    LOG_FILE.parent.mkdir(exist_ok=True)


def log_analysis(
    transcript_length: int,
    language: str,
    provider: str,
    duration_ms: float,
    result: dict,
    error: str = None
):
    """Log every analysis run with key metrics."""
    _ensure_log_dir()

    # Extract key metrics from result
    hallucination_rate = 0.0
    flagged_count      = 0
    risk_label         = "UNKNOWN"
    soft_rejection_risk = "NONE"

    if result:
        verification = result.get("verification", {})
        ai_check = verification.get("action_items", {})
        flagged_count      = ai_check.get("flagged_count", 0)
        hallucination_rate = ai_check.get("hallucination_rate", 0.0)
        risk_label         = verification.get("risk_label", "UNKNOWN")
        soft_rejections    = result.get("soft_rejections", {})
        soft_rejection_risk = soft_rejections.get("risk_level", "NONE")

    entry = {
        "timestamp":          datetime.now().isoformat(),
        "transcript_chars":   transcript_length,
        "language":           language,
        "provider":           provider,
        "duration_ms":        round(duration_ms, 1),
        "summary_bullets":    len(result.get("summary", [])) if result else 0,
        "action_items_total": len(result.get("action_items", [])) if result else 0,
        "action_items_flagged": flagged_count,
        "hallucination_rate": hallucination_rate,
        "hallucination_risk": risk_label,
        "soft_rejection_risk": soft_rejection_risk,
        "speakers_detected":  len(result.get("speakers", [])) if result else 0,
        "keigo_level":        result.get("japan_insights", {}).get("keigo_level", "unknown") if result else "unknown",
        "code_switches":      result.get("japan_insights", {}).get("code_switch_count", 0) if result else 0,
        "error":              error,
        "status":             "error" if error else "success"
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def log_error(error_type: str, message: str, context: dict = None):
    """Log errors with context for debugging."""
    _ensure_log_dir()
    entry = {
        "timestamp":  datetime.now().isoformat(),
        "type":       "error",
        "error_type": error_type,
        "message":    message,
        "context":    context or {}
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def get_stats(last_n: int = 100) -> dict:
    """
    Returns performance stats from last N analyses.
    Shows: avg duration, error rate, hallucination rate, provider breakdown.
    """
    _ensure_log_dir()
    if not LOG_FILE.exists():
        return {"message": "No logs yet"}

    entries = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entries.append(json.loads(line.strip()))
            except Exception:
                continue

    # Take last N
    entries = [e for e in entries if e.get("status") == "success"][-last_n:]
    if not entries:
        return {"message": "No successful analyses logged"}

    total          = len(entries)
    avg_duration   = round(sum(e.get("duration_ms", 0) for e in entries) / total, 1)
    error_count    = sum(1 for e in entries if e.get("error"))
    halluc_rates   = [e.get("hallucination_rate", 0) for e in entries]
    avg_halluc     = round(sum(halluc_rates) / len(halluc_rates), 3) if halluc_rates else 0

    providers = {}
    for e in entries:
        p = e.get("provider", "unknown")
        providers[p] = providers.get(p, 0) + 1

    high_risk = sum(1 for e in entries if e.get("hallucination_risk") in ("HIGH", "MEDIUM"))

    return {
        "total_analyses":         total,
        "avg_duration_ms":        avg_duration,
        "error_rate":             round(error_count / total, 3),
        "avg_hallucination_rate": avg_halluc,
        "high_risk_analyses":     high_risk,
        "provider_breakdown":     providers,
        "languages": {
            lang: sum(1 for e in entries if e.get("language") == lang)
            for lang in set(e.get("language", "unknown") for e in entries)
        }
    }


if __name__ == "__main__":
    # Simulate some log entries
    log_analysis(1500, "mixed", "ollama", 95000, {
        "summary": ["a", "b", "c"],
        "action_items": [{"task": "test", "hallucination_flag": False}],
        "speakers": [{"name": "Tanaka"}],
        "japan_insights": {"keigo_level": "high", "code_switch_count": 5},
        "verification": {"action_items": {"flagged_count": 0, "hallucination_rate": 0.0}, "risk_label": "LOW"},
        "soft_rejections": {"risk_level": "MEDIUM"}
    })
    print(json.dumps(get_stats(), indent=2))