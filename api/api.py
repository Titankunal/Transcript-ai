# api.py
# FastAPI REST API for TranscriptAI — v2
#
# v2 FIXES:
#   FIX-1: analyze_transcript() wrapped in asyncio.to_thread() — was blocking
#           the entire FastAPI event loop on every request (sync call inside async route).
#           Now truly non-blocking: multiple users can hit /analyze simultaneously.
#   FIX-2: utils import path corrected (was utils.utils, now utils directly).
#   FIX-3: Temperature 0.1 + top_p 0.85 applied in analyzer.py — api.py inherits
#           these automatically since it calls analyze_transcript().
#   FIX-4: Batch endpoint now uses asyncio.gather() for true parallel execution
#           instead of sequential await in a loop.
#
# Run with:
#   pip install fastapi uvicorn httpx
#   uvicorn api:app --reload --port 8000
#
# Docs: http://localhost:8000/docs

import asyncio
import uuid
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from analysis.analyzer import analyze_transcript
from utils import detect_language, clean_text

# ── Optional modules ──────────────────────────────────────────────────────────
try:
    from transcription.pii_masker import mask_transcript, restore_pii_in_result, get_pii_report
    PII_AVAILABLE = True
except ImportError:
    PII_AVAILABLE = False

try:
    from analysis.soft_rejection_detector import detect_soft_rejections
    SOFT_REJECTION_AVAILABLE = True
except ImportError:
    SOFT_REJECTION_AVAILABLE = False

try:
    from analysis.hallucination_guard import verify_result
    HALLUCINATION_GUARD_AVAILABLE = True
except ImportError:
    HALLUCINATION_GUARD_AVAILABLE = False

# ── APP SETUP ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="TranscriptAI API",
    description=(
        "Japanese Business Intelligence — Meeting Transcript Analyzer. "
        "Extracts action items, sentiment, speaker breakdown, and Japan-specific "
        "insights. APPI compliant via local PII masking before any LLM call."
    ),
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── REQUEST / RESPONSE MODELS ─────────────────────────────────────────────────
class AnalyzeRequest(BaseModel):
    transcript: str = Field(
        ...,
        min_length=20,
        description="Meeting transcript. Supports Japanese, English, Hindi, mixed."
    )
    language: Optional[str] = Field(
        None,
        description="Force language: 'ja', 'en', 'hi', 'mixed'. Null = auto-detect."
    )
    mask_pii: bool = Field(
        True,
        description="Anonymize PII before LLM (APPI compliance). Recommended: true."
    )
    include_soft_rejections: bool = Field(
        True,
        description="Detect indirect rejection patterns in Japanese speech."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "transcript": "田中: おはようございます。\nSato: Good morning. The Q3 report is ready.",
                "language": None,
                "mask_pii": True,
                "include_soft_rejections": True
            }
        }


class AnalyzeResponse(BaseModel):
    request_id:         str
    timestamp:          str
    language_detected:  str
    pii_masked:         bool
    pii_items_found:    int
    processing_time_ms: float
    result:             dict


# ── HEALTH CHECK ──────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    """Check API status and available modules."""
    import os
    groq_key_present = bool(os.getenv("GROQ_API_KEY", "").strip())
    return {
        "status":   "healthy",
        "version":  "2.0.0",
        "modules":  {
            "pii_masker":          PII_AVAILABLE,
            "soft_rejection":      SOFT_REJECTION_AVAILABLE,
            "hallucination_guard": HALLUCINATION_GUARD_AVAILABLE,
        },
        "provider":       "groq" if groq_key_present else "mock",
        "groq_key":       groq_key_present,
        "appi_compliant": PII_AVAILABLE,
        "async_mode":     True,
    }


# ── SINGLE ANALYZE ENDPOINT ───────────────────────────────────────────────────
@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    """
    Analyze a meeting transcript — returns structured intelligence.

    Non-blocking: uses asyncio.to_thread() so multiple requests run concurrently.
    analyze_transcript() itself is CPU/IO-bound sync code — thread pool handles it.
    """
    start_time = datetime.now()
    request_id = str(uuid.uuid4())[:8]

    # Clean and validate
    transcript = clean_text(request.transcript)
    if len(transcript.strip()) < 20:
        raise HTTPException(
            status_code=400,
            detail="Transcript too short (minimum 20 characters after cleaning)"
        )

    # Detect language
    detected_lang = detect_language(transcript)
    active_lang   = request.language or detected_lang

    # PII masking — runs locally before any LLM call
    pii_items_found = 0
    pii_mask        = None
    text_to_analyze = transcript

    if request.mask_pii and PII_AVAILABLE:
        # mask_transcript is fast/sync — ok to call directly
        text_to_analyze, pii_mask = mask_transcript(transcript)
        pii_report      = get_pii_report(pii_mask)
        pii_items_found = pii_report.get("total_pii_found", 0)

    # FIX-1: Run blocking analyze_transcript in thread pool
    # This is the key async fix — Groq HTTP call is I/O bound but uses
    # requests (sync). asyncio.to_thread() offloads it without blocking
    # the event loop, so concurrent users don't queue behind each other.
    try:
        result = await asyncio.to_thread(
            analyze_transcript,
            text_to_analyze,
            active_lang
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    # Restore PII in results (local operation, fast)
    if pii_mask is not None:
        result = restore_pii_in_result(result, pii_mask)

    # Soft rejection detection (local pattern matching, fast)
    if request.include_soft_rejections and SOFT_REJECTION_AVAILABLE:
        result["soft_rejections"] = detect_soft_rejections(transcript)

    elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000

    return AnalyzeResponse(
        request_id          = request_id,
        timestamp           = datetime.now().isoformat(),
        language_detected   = active_lang,
        pii_masked          = request.mask_pii and PII_AVAILABLE,
        pii_items_found     = pii_items_found,
        processing_time_ms  = round(elapsed_ms, 1),
        result              = result
    )


# ── BATCH ENDPOINT ────────────────────────────────────────────────────────────
@app.post("/analyze/batch")
async def analyze_batch(requests: list[AnalyzeRequest]):
    """
    Analyze multiple transcripts in parallel.

    FIX-4: Uses asyncio.gather() for true concurrent execution.
    Was previously sequential (await in loop) — now all run simultaneously.
    Max 10 per batch. For 10,000+/day use Redis Queue + vLLM.
    """
    if len(requests) > 10:
        raise HTTPException(
            status_code=400,
            detail="Batch limit is 10. For larger volumes use the async job queue."
        )

    # FIX-4: gather runs all requests concurrently, not one by one
    async def _safe_analyze(req: AnalyzeRequest) -> dict:
        try:
            result = await analyze(req)
            return {"status": "success", "data": result.dict()}
        except HTTPException as e:
            return {"status": "error", "error": e.detail}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    results = await asyncio.gather(*[_safe_analyze(req) for req in requests])

    return {
        "batch_size": len(requests),
        "successful": sum(1 for r in results if r["status"] == "success"),
        "failed":     sum(1 for r in results if r["status"] == "error"),
        "results":    list(results)
    }


# ── PATTERNS ENDPOINT ─────────────────────────────────────────────────────────
@app.get("/patterns/soft-rejections")
async def get_soft_rejection_patterns():
    """Returns the full soft rejection pattern dictionary with cultural explanations."""
    if not SOFT_REJECTION_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="soft_rejection_detector.py not found"
        )
    from analysis.soft_rejection_detector import SOFT_REJECTION_PATTERNS
    return {
        "total_patterns": len(SOFT_REJECTION_PATTERNS),
        "patterns":       SOFT_REJECTION_PATTERNS,
        "cultural_context": (
            "Japanese business communication avoids direct refusal. "
            "These patterns encode the speaker's true intent through indirect language. "
            "Examples: 検討いたします (likely rejection), 難しいかもしれません (high rejection signal)."
        )
    }


# ── RUN ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)