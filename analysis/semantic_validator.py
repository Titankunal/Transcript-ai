# semantic_validator.py — v2
# Semantic validation of action items using sentence-transformers
#
# V2 FIX: Lazy model loading — SentenceTransformer is NOT loaded at module
# import time. Previously it loaded on every app start, causing:
#   RuntimeError: Cannot send a request, as the client has been closed.
# when HuggingFace was unreachable (no internet, cold start, httpx closed).
# Now loads on first actual use only. App starts instantly regardless.

import re

# ── LAZY MODEL SINGLETON ──────────────────────────────────────────────────────
_ST_MODEL = None          # None = not yet loaded
_ST_AVAILABLE = None      # None = not yet checked, True/False = checked


def _get_model():
    """
    Lazy-load SentenceTransformer on first use.
    Returns model or None if unavailable.
    Never raises — falls back to token overlap silently.
    """
    global _ST_MODEL, _ST_AVAILABLE

    if _ST_AVAILABLE is False:
        return None          # already confirmed unavailable
    if _ST_MODEL is not None:
        return _ST_MODEL     # already loaded

    try:
        from sentence_transformers import SentenceTransformer
        # Use local_files_only=True first — avoids network call if cached
        try:
            _ST_MODEL = SentenceTransformer(
                "paraphrase-multilingual-MiniLM-L12-v2",
                local_files_only=True
            )
        except Exception:
            # Not cached locally — try downloading
            _ST_MODEL = SentenceTransformer(
                "paraphrase-multilingual-MiniLM-L12-v2"
            )
        _ST_AVAILABLE = True
        return _ST_MODEL
    except Exception:
        _ST_AVAILABLE = False
        return None


# ── SEMANTIC VALIDATION ───────────────────────────────────────────────────────

def _token_overlap(a: str, b: str) -> float:
    """Fallback: simple token overlap when model unavailable."""
    a_tokens = set(re.findall(r'\w+', a.lower()))
    b_tokens = set(re.findall(r'\w+', b.lower()))
    if not a_tokens or not b_tokens:
        return 0.0
    return len(a_tokens & b_tokens) / max(len(a_tokens), len(b_tokens))


def _semantic_similarity(text_a: str, text_b: str) -> float:
    """
    Compute semantic similarity between two strings.
    Uses sentence-transformers if available, else token overlap fallback.
    """
    model = _get_model()
    if model is None:
        return _token_overlap(text_a, text_b)

    try:
        import numpy as np
        embeddings = model.encode([text_a, text_b], convert_to_numpy=True)
        # Cosine similarity
        a, b = embeddings[0], embeddings[1]
        norm = (np.linalg.norm(a) * np.linalg.norm(b))
        if norm == 0:
            return 0.0
        return float(np.dot(a, b) / norm)
    except Exception:
        return _token_overlap(text_a, text_b)


def validate_action_items_semantic(
    action_items: list,
    transcript: str,
    threshold: float = 0.35,
) -> list:
    """
    Semantic validation of action items against the source transcript.

    For each action item:
    - Compute similarity between the task text and all transcript sentences
    - If best similarity >= threshold: mark as semantically grounded
    - If below threshold but rule-based hallucination_flag=True: rescue if
      token overlap is reasonable (prevents TF-IDF false flags)

    Falls back to token overlap silently if sentence-transformers unavailable.
    Returns the same list with semantic_grounding scores added.
    """
    if not action_items:
        return action_items

    # Split transcript into sentences for per-sentence comparison
    sentences = [s.strip() for s in re.split(r'[.!?。！？\n]+', transcript) if s.strip()]
    if not sentences:
        return action_items

    validated = []
    for item in action_items:
        task = item.get("task", "")
        if not task or task.startswith("⚠️"):
            validated.append(item)
            continue

        # Find best matching sentence in transcript
        best_score = 0.0
        for sentence in sentences:
            score = _semantic_similarity(task, sentence)
            if score > best_score:
                best_score = score

        item["semantic_grounding"] = round(best_score, 3)

        # Rescue false-flagged items if semantically grounded
        if item.get("hallucination_flag") and best_score >= threshold:
            item["hallucination_flag"] = False
            item["flag_reason"]        = None
            item["rescued_by"]         = "semantic_validation"

        validated.append(item)

    return validated


def is_model_loaded() -> bool:
    """Returns True if the sentence-transformer model is loaded and ready."""
    return _ST_MODEL is not None


def model_status() -> str:
    """Human-readable model status for diagnostics."""
    if _ST_AVAILABLE is None:
        return "not_checked"
    if _ST_AVAILABLE:
        return "loaded"
    return "unavailable_using_fallback"