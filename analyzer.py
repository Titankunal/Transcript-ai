# analyzer.py
# Core AI analysis pipeline for TranscriptAI
#
# ── PROVIDER STRATEGY ────────────────────────────────────────────────────────
#
#   LOCAL (default):   Ollama + qwen3:8b
#                      Zero cost, APPI compliant, 60-120 sec/analysis
#                      Best for: development, sensitive data, no internet
#
#   CLOUD FREE:        Groq API + llama-3.1-8b-instant
#                      Zero cost (500 req/day free tier), ~3 sec/analysis
#                      Best for: deployed version, demos, interviews
#                      Get free key: console.groq.com → API Keys
#
#   SWAP IN ONE LINE:  Change PROVIDER = "ollama" to PROVIDER = "groq"
#                      Nothing else changes. JSON schema is identical.
#
# ── INTERVIEW ANSWER ──────────────────────────────────────────────────────────
#   "I chose Ollama for zero cost and APPI compliance during development.
#    For production speed I use Groq's free tier — same zero cost,
#    10x faster, and the provider swap is literally one line change
#    because the JSON schema contract is identical."
# ─────────────────────────────────────────────────────────────────────────────

import json
import os
import re
import requests

# ── CONFIG ────────────────────────────────────────────────────────────────────
# Change this one line to switch providers:
PROVIDER = os.getenv("TRANSCRIPT_AI_PROVIDER", "ollama")  # "ollama" | "groq"

# Ollama settings (local, free)
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen3:8b"

# Groq settings (cloud, free tier)
# Get your free key at: https://console.groq.com
# Set env var: GROQ_API_KEY=your_key_here
# Or add to .streamlit/secrets.toml: GROQ_API_KEY = "your_key_here"
GROQ_URL   = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"   # free, fast, strong JA/EN
# ─────────────────────────────────────────────────────────────────────────────


def _summary_instruction(text: str) -> str:
    """Dynamic summary length based on transcript word count."""
    words = len(text.split())
    if words < 200:
        return "summary: write 3 concise bullet points covering the key topics"
    elif words < 600:
        return "summary: write 5 concise bullet points covering ALL key topics discussed"
    elif words < 1200:
        return "summary: write 7 concise bullet points — cover every major topic, decision, and outcome"
    else:
        return (
            "summary: write as many bullet points as needed (minimum 8) to fully cover "
            "every major topic, decision, concern, and outcome. Do NOT compress multiple topics into one bullet."
        )


def build_prompt(text: str, language: str) -> str:
    lang_hint = (
        "The transcript may contain Japanese (日本語) and English mixed together. "
        "Detect and handle both. Extract Japanese phrases as-is for nemawashi signals."
        if language in ("ja", "mixed")
        else "The transcript is in English."
    )
    summary_rule = _summary_instruction(text)

    return f"""You are an expert meeting analyst specializing in Japanese business culture.
{lang_hint}

Analyze the transcript and return ONLY a valid JSON object.
No explanation, no markdown, no backticks — raw JSON only.

Schema:
{{
  "summary": ["bullet 1", "bullet 2", "...as many as needed"],
  "action_items": [
    {{"task": "description", "owner": "person name", "deadline": "date or 'Not specified'"}}
  ],
  "sentiment": [
    {{"speaker": "name", "score": "positive|neutral|negative", "label": "brief reason"}}
  ],
  "speakers": [
    {{"name": "name", "talk_time_pct": 50, "tone": "formal|casual|mixed"}}
  ],
  "japan_insights": {{
    "keigo_level": "high|medium|low",
    "nemawashi_signals": ["actual phrase from transcript"],
    "code_switch_count": 0
  }}
}}

Rules:
- {summary_rule}
- action_items: list EVERY task, request, or commitment — even implied ones
- sentiment: one entry per unique speaker
- speakers: talk_time_pct values must sum to 100
- nemawashi_signals: actual phrases showing indirect agreement/hesitation/soft refusal
- code_switch_count: count JA↔EN language switches
- Return ONLY the JSON. No other text.

TRANSCRIPT:
{text}
"""


def _call_ollama(prompt: str, max_tokens: int) -> str:
    """Call local Ollama. Returns raw response string."""
    response = requests.post(
        OLLAMA_URL,
        json={
            "model":  OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2, "num_predict": max_tokens},
            "think":  False
        },
        timeout=300
    )
    response.raise_for_status()
    return response.json().get("response", "")


def _call_groq(prompt: str, max_tokens: int) -> str:
    """
    Call Groq free API. Returns raw response string.
    Free tier: 500 requests/day, ~3 sec response time.
    Get key: https://console.groq.com
    """
    api_key = os.getenv("GROQ_API_KEY") or os.getenv("groq_api_key")

    # Also try Streamlit secrets
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets.get("GROQ_API_KEY", "")
        except Exception:
            pass

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found. "
            "Set env var: export GROQ_API_KEY=your_key "
            "Or add to .streamlit/secrets.toml: GROQ_API_KEY = 'your_key' "
            "Get free key at: https://console.groq.com"
        )

    response = requests.post(
        GROQ_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type":  "application/json"
        },
        json={
            "model":       GROQ_MODEL,
            "messages":    [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "max_tokens":  max_tokens,
        },
        timeout=30   # Groq is fast — 30 sec is generous
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def _mock_response(text: str) -> dict:
    """
    Realistic mock data when no LLM is available (Streamlit Cloud without API key).
    Scales summary bullets with transcript length.
    """
    words = len(text.split())
    if words < 200:
        summary = [
            "The team discussed Q3 project progress and confirmed key deadlines.",
            "Action items were assigned with clear ownership and timelines.",
            "Both speakers demonstrated collaborative tone with mixed JA/EN communication."
        ]
    elif words < 600:
        summary = [
            "The meeting opened with a Q3 progress review showing KPI performance at 98% of target.",
            "Concerns were raised about the new feature release schedule and potential delays.",
            "Budget adjustments were discussed and require sign-off from the technical team.",
            "Action items were clearly assigned with deadlines ranging from today to next Friday.",
            "Next meeting scheduled for Friday at 15:00 — minutes to be prepared by Tanaka."
        ]
    else:
        summary = [
            "The meeting opened with a Q3 progress review showing KPI performance at 98% of target.",
            "Concerns were raised about the new feature release schedule.",
            "鈴木 expressed indirect hesitation using nemawashi language.",
            "Budget adjustments require final confirmation from the technical team by Monday.",
            "Customer feedback volume has increased — support team expansion proposed.",
            "Support manual revision identified as a parallel workstream.",
            "All action items formally assigned with clear owners and deadlines.",
            "Next sync confirmed for Friday 15:00 — Tanaka responsible for minutes."
        ]

    return {
        "summary": summary,
        "action_items": [
            {"task": "Confirm release schedule", "owner": "Suzuki", "deadline": "Monday"},
            {"task": "Review Q3 report financial section", "owner": "Tanaka", "deadline": "Thursday"},
            {"task": "Send delay notification to client", "owner": "Sato", "deadline": "Today"},
            {"task": "Draft support manual revision", "owner": "Suzuki", "deadline": "Friday"},
            {"task": "Prepare meeting minutes", "owner": "Tanaka", "deadline": "Friday 15:00"}
        ],
        "sentiment": [
            {"speaker": "Tanaka", "score": "positive", "label": "Professional and collaborative"},
            {"speaker": "Suzuki", "score": "neutral",  "label": "Cautiously cooperative"}
        ],
        "speakers": [
            {"name": "Tanaka", "talk_time_pct": 55, "tone": "formal"},
            {"name": "Suzuki", "talk_time_pct": 45, "tone": "formal"}
        ],
        "japan_insights": {
            "keigo_level": "high",
            "nemawashi_signals": ["そうですね", "検討いたします", "難しいかもしれません", "前向きに対応"],
            "code_switch_count": 4
        }
    }


def analyze_transcript(text: str, language: str = "en") -> dict:
    """
    Analyzes a transcript using the configured LLM provider.

    Provider selection (PROVIDER env var or config above):
      "ollama" → local Ollama (default, zero cost, APPI compliant)
      "groq"   → Groq free API (zero cost, 10x faster, needs GROQ_API_KEY)

    Falls back to mock data if no LLM is reachable.

    JSON schema is IDENTICAL regardless of provider.
    Swapping providers requires changing one line — nothing else.
    """
    prompt     = build_prompt(text, language)
    max_tokens = min(2048, max(1024, len(text.split()) * 3))

    raw = ""
    provider_used = PROVIDER

    try:
        if PROVIDER == "groq":
            raw = _call_groq(prompt, max_tokens)
        else:
            raw = _call_ollama(prompt, max_tokens)

        # Strip qwen3 thinking blocks and markdown fences
        raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL)
        raw = re.sub(r"```(?:json)?", "", raw).strip()

        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            raise ValueError("No JSON object in model response")

        result = json.loads(match.group())
        result = _validate_and_fill(result)

        # Fix 1: rule-based code-switch (overrides LLM count)
        try:
            from evaluator import count_code_switches
            result["japan_insights"]["code_switch_count"] = count_code_switches(text)
            result["japan_insights"]["code_switch_source"] = "rule_based"
        except ImportError:
            pass

        # Fix 2: hallucination prevention (rule-based, NOT LLM)
        try:
            from hallucination_guard import verify_result
            result = verify_result(result, text)
        except ImportError:
            pass

        # Fix 3: soft rejection detection
        try:
            from soft_rejection_detector import detect_soft_rejections
            result["soft_rejections"] = detect_soft_rejections(text)
        except ImportError:
            pass

        result["_provider"] = provider_used
        return result

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        # Ollama not running — fall back to mock
        result = _mock_response(text)
        result["_provider"] = "mock"
        return result

    except ValueError as e:
        if "GROQ_API_KEY" in str(e):
            # No Groq key — fall back to mock
            result = _mock_response(text)
            result["_provider"] = "mock_no_key"
            return result
        raise

    except json.JSONDecodeError as e:
        raise ValueError(f"Model returned invalid JSON: {e}\n\nRaw:\n{raw[:500]}")


def _validate_and_fill(data: dict) -> dict:
    """Ensure all required keys exist with sensible defaults."""
    data.setdefault("summary", ["No summary available."])
    data.setdefault("action_items", [])
    data.setdefault("sentiment", [])
    data.setdefault("speakers", [])
    data.setdefault("japan_insights", {})

    ji = data["japan_insights"]
    ji.setdefault("keigo_level", "unknown")
    ji.setdefault("nemawashi_signals", [])
    ji.setdefault("code_switch_count", 0)

    speakers = data["speakers"]
    if speakers:
        total = sum(s.get("talk_time_pct", 0) for s in speakers)
        if total > 0 and total != 100:
            for s in speakers:
                s["talk_time_pct"] = round(s.get("talk_time_pct", 0) * 100 / total)

    return data


# ── QUICK TEST ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    # Allow testing Groq: python analyzer.py groq
    if len(sys.argv) > 1 and sys.argv[1] == "groq":
        os.environ["TRANSCRIPT_AI_PROVIDER"] = "groq"
        print("Testing with Groq provider...")
    else:
        print(f"Testing with {PROVIDER} provider...")

    sample = """
    田中: おはようございます。今日のプロジェクト更新について話しましょう。
    Sato: Good morning. Yes, the Q3 report is almost ready.
    田中: そうですね。Deadline is next Friday, right?
    Sato: Correct. I will handle the financial section. Can you review by Thursday?
    田中: 検討します。Also, we need to inform the client about the delay.
    Sato: Understood. I will send them an email today.
    田中: ありがとうございます。Let's sync again tomorrow morning.
    """
    result = analyze_transcript(sample, language="mixed")
    print(f"Provider used: {result.get('_provider', 'unknown')}")
    print(json.dumps(result, indent=2, ensure_ascii=False))