"""
TranscriptAI smoke tests — no API keys, no ML models required.
"""
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


# ── PII Masker ────────────────────────────────────────────────────────────────

def test_pii_masks_email():
    from transcription.pii_masker import mask_transcript
    masked, pii = mask_transcript("Contact kunal@example.com for info.")
    assert "kunal@example.com" not in masked

def test_pii_masks_phone():
    from transcription.pii_masker import mask_transcript
    masked, pii = mask_transcript("Call +91-9876543210 now.")
    assert "9876543210" not in masked

def test_pii_empty_string():
    from transcription.pii_masker import mask_transcript
    masked, pii = mask_transcript("")
    assert masked == "" or masked is not None  # empty input returns safely

def test_pii_report_is_dict():
    from transcription.pii_masker import mask_transcript, get_pii_report
    _, pii = mask_transcript("Email billing@acme.co for invoice.")
    report = get_pii_report(pii)
    assert isinstance(report, dict)

def test_pii_mask_object_created():
    from transcription.pii_masker import mask_transcript, PIIMask
    _, pii = mask_transcript("Send to admin@corp.jp")
    assert isinstance(pii, PIIMask)


# ── Hallucination Guard ───────────────────────────────────────────────────────

def test_hallucination_verify_result_returns_dict():
    from analysis.hallucination_guard import verify_result
    fake_result = {
        "summary": ["The meeting discussed budget."],
        "action_items": [],
        "sentiment_by_speaker": []
    }
    transcript = "We discussed the Q3 budget in the meeting."
    result = verify_result(fake_result, transcript)
    assert isinstance(result, dict)

def test_hallucination_verify_summary_valid():
    from analysis.hallucination_guard import verify_summary
    summary = ["Meeting was about budget planning."]
    transcript = "Today we discussed budget planning for Q3."
    result = verify_summary(summary, transcript)
    assert isinstance(result, dict)

def test_hallucination_verify_action_items_empty():
    from analysis.hallucination_guard import verify_action_items
    result = verify_action_items([], "Some transcript text here.")
    assert isinstance(result, dict)

def test_hallucination_verify_action_items_fabricated():
    from analysis.hallucination_guard import verify_action_items
    items = [{"task": "Hire 500 engineers by tomorrow", "owner": "unknown"}]
    transcript = "We briefly discussed the Q3 report."
    result = verify_action_items(items, transcript)
    assert isinstance(result, dict)


# ── Soft Rejection Detector ───────────────────────────────────────────────────

def test_soft_rejection_returns_dict():
    from analysis.soft_rejection_detector import detect_soft_rejections
    result = detect_soft_rejections("Yes, we can deliver by Friday.")
    assert isinstance(result, dict)

def test_soft_rejection_japanese_detected():
    from analysis.soft_rejection_detector import detect_soft_rejections
    # Classic nemawashi — "this might be a bit difficult"
    result = detect_soft_rejections("少し難しいかもしれません。ちょっと検討させてください。")
    assert isinstance(result, dict)

def test_soft_rejection_has_expected_keys():
    from analysis.soft_rejection_detector import detect_soft_rejections
    result = detect_soft_rejections("We will look into it and get back to you.")
    # Must return at least one of these standard keys
    assert any(k in result for k in ["soft_rejections", "patterns", "detected", "has_soft_rejection", "count"])

def test_soft_rejection_empty_transcript():
    from analysis.soft_rejection_detector import detect_soft_rejections
    result = detect_soft_rejections("")
    assert isinstance(result, dict)


# ── Cache ─────────────────────────────────────────────────────────────────────

def test_cache_set_and_get():
    from utils.cache import set_cache, get_cached
    set_cache("Hello world test", "en", {"status": "ok"})
    val = get_cached("Hello world test", "en")
    assert val is not None
    assert val["status"] == "ok"

def test_cache_miss_returns_none():
    from utils.cache import get_cached
    val = get_cached("definitely not cached xyz 999", "en")
    assert val is None

def test_cache_stats_is_dict():
    from utils.cache import get_cache_stats
    stats = get_cache_stats()
    assert isinstance(stats, dict)

def test_cache_overwrite():
    from utils.cache import set_cache, get_cached
    set_cache("overwrite test transcript", "en", {"v": 1})
    set_cache("overwrite test transcript", "en", {"v": 2})
    val = get_cached("overwrite test transcript", "en")
    assert val["v"] == 2


# ── Speaker Normalizer ────────────────────────────────────────────────────────

def test_normalize_speaker_name_returns_string():
    from transcription.speaker_normalizer import normalize_speaker_name
    result = normalize_speaker_name("田中")
    assert isinstance(result, str)
    assert len(result) > 0

def test_normalize_speaker_name_english():
    from transcription.speaker_normalizer import normalize_speaker_name
    result = normalize_speaker_name("Alice")
    assert isinstance(result, str)

def test_extract_all_speakers_returns_dict():
    from transcription.speaker_normalizer import extract_all_speakers
    transcript = "Alice: Let's discuss. Bob: Agreed. Alice: Great."
    result = extract_all_speakers(transcript)
    assert isinstance(result, dict)

def test_extract_all_speakers_empty():
    from transcription.speaker_normalizer import extract_all_speakers
    result = extract_all_speakers("")
    assert isinstance(result, dict)