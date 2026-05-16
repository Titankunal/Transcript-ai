"""
TranscriptAI smoke tests — no API keys, no ML models required.
"""
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


# ── PII Masker ────────────────────────────────────────────────────────────────

def test_pii_masks_email():
    from transcription.pii_masker import PIIMasker
    masker = PIIMasker()
    masked, mapping = masker.mask("Contact kunal@example.com for info.")
    assert "kunal@example.com" not in masked

def test_pii_masks_phone():
    from transcription.pii_masker import PIIMasker
    masker = PIIMasker()
    masked, mapping = masker.mask("Call +91-9876543210 now.")
    assert "9876543210" not in masked

def test_pii_restore_roundtrip():
    from transcription.pii_masker import PIIMasker
    masker = PIIMasker()
    original = "Email billing@acme.co for invoice."
    masked, mapping = masker.mask(original)
    restored = masker.restore(masked, mapping)
    assert "billing@acme.co" in restored

def test_pii_empty_string():
    from transcription.pii_masker import PIIMasker
    masker = PIIMasker()
    masked, mapping = masker.mask("")
    assert masked == ""


# ── Hallucination Guard ───────────────────────────────────────────────────────

def test_hallucination_valid_claim():
    from analysis.hallucination_guard import HallucinationGuard
    guard = HallucinationGuard()
    transcript = "The meeting is on Monday at 3pm in Tokyo."
    claim = "Meeting scheduled for Monday."
    result = guard.verify(claim, transcript)
    assert result["verified"] is True

def test_hallucination_invalid_claim():
    from analysis.hallucination_guard import HallucinationGuard
    guard = HallucinationGuard()
    transcript = "We discussed the Q3 budget briefly."
    claim = "Team agreed to hire 50 engineers immediately."
    result = guard.verify(claim, transcript)
    assert result["verified"] is False

def test_hallucination_returns_dict():
    from analysis.hallucination_guard import HallucinationGuard
    guard = HallucinationGuard()
    result = guard.verify("Some claim.", "Some transcript.")
    assert isinstance(result, dict)
    assert "verified" in result


# ── Soft Rejection Detector ───────────────────────────────────────────────────

def test_soft_rejection_japanese():
    from analysis.soft_rejection_detector import SoftRejectionDetector
    detector = SoftRejectionDetector()
    result = detector.detect("少し難しいかもしれません", language="ja")
    assert result["has_soft_rejection"] is True

def test_soft_rejection_direct_english():
    from analysis.soft_rejection_detector import SoftRejectionDetector
    detector = SoftRejectionDetector()
    result = detector.detect("Yes, we can deliver by Friday.", language="en")
    assert result["has_soft_rejection"] is False

def test_soft_rejection_confidence_range():
    from analysis.soft_rejection_detector import SoftRejectionDetector
    detector = SoftRejectionDetector()
    result = detector.detect("We will look into it.", language="en")
    assert "confidence" in result
    assert 0.0 <= result["confidence"] <= 1.0


# ── Cache ─────────────────────────────────────────────────────────────────────

def test_cache_set_and_get():
    from utils.cache import Cache
    cache = Cache()
    cache.set("key_smoke_001", {"status": "ok"})
    val = cache.get("key_smoke_001")
    assert val is not None
    assert val["status"] == "ok"

def test_cache_miss_returns_none():
    from utils.cache import Cache
    cache = Cache()
    val = cache.get("definitely_missing_key_xyz")
    assert val is None

def test_cache_overwrite():
    from utils.cache import Cache
    cache = Cache()
    cache.set("key_overwrite", {"v": 1})
    cache.set("key_overwrite", {"v": 2})
    assert cache.get("key_overwrite")["v"] == 2


# ── Speaker Normalizer ────────────────────────────────────────────────────────

def test_speaker_normalizer_empty():
    from transcription.speaker_normalizer import SpeakerNormalizer
    norm = SpeakerNormalizer()
    result = norm.normalize([])
    assert result == {}

def test_speaker_normalizer_single():
    from transcription.speaker_normalizer import SpeakerNormalizer
    norm = SpeakerNormalizer()
    result = norm.normalize(["Alice"])
    assert "Alice" in result

def test_speaker_normalizer_returns_dict():
    from transcription.speaker_normalizer import SpeakerNormalizer
    norm = SpeakerNormalizer()
    result = norm.normalize(["Bob", "Robert"])
    assert isinstance(result, dict)