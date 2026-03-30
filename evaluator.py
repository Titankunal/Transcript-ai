# evaluator.py
# Evaluation layer for TranscriptAI
# Measures: ROUGE (summary), F1 (action items), Accuracy (sentiment), Rule-based (Japan insights)

import re
from typing import Any


# ── ROUGE-1 (simple word overlap) ────────────────────────────────────────────
def _tokenize(text: str) -> set:
    """Lowercase, remove punctuation, split into words."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return set(text.split())


def rouge1_score(prediction: str, reference: str) -> dict:
    """
    Computes ROUGE-1 precision, recall, and F1 between two strings.
    Used for evaluating meeting summaries.
    """
    pred_tokens = _tokenize(prediction)
    ref_tokens = _tokenize(reference)

    if not pred_tokens or not ref_tokens:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

    overlap = pred_tokens & ref_tokens
    precision = len(overlap) / len(pred_tokens)
    recall = len(overlap) / len(ref_tokens)
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    return {
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3)
    }


def evaluate_summary(pred_bullets: list, ref_bullets: list) -> dict:
    """
    Evaluates summary quality by averaging ROUGE-1 F1 across all bullet pairs.
    """
    if not pred_bullets or not ref_bullets:
        return {"avg_rouge1_f1": 0.0, "per_bullet": []}

    scores = []
    for i, ref in enumerate(ref_bullets):
        pred = pred_bullets[i] if i < len(pred_bullets) else ""
        score = rouge1_score(pred, ref)
        scores.append(score)

    avg_f1 = round(sum(s["f1"] for s in scores) / len(scores), 3)
    return {
        "avg_rouge1_f1": avg_f1,
        "per_bullet": scores,
        "grade": _grade(avg_f1)
    }


# ── F1 FOR ACTION ITEMS ───────────────────────────────────────────────────────
def _normalize(text: str) -> str:
    return text.lower().strip()


def evaluate_action_items(pred_items: list, ref_items: list) -> dict:
    """
    Evaluates action item extraction using F1 score.
    Matches predicted tasks against reference tasks by keyword overlap.
    """
    if not ref_items:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0, "grade": "N/A"}

    matched = 0
    for ref in ref_items:
        ref_words = _tokenize(ref.get("task", ""))
        for pred in pred_items:
            pred_words = _tokenize(pred.get("task", ""))
            overlap = ref_words & pred_words
            # Match if >40% word overlap
            if len(ref_words) > 0 and len(overlap) / len(ref_words) >= 0.4:
                matched += 1
                break

    precision = matched / len(pred_items) if pred_items else 0.0
    recall = matched / len(ref_items) if ref_items else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    return {
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "matched": matched,
        "predicted": len(pred_items),
        "expected": len(ref_items),
        "grade": _grade(f1)
    }


# ── SENTIMENT ACCURACY ───────────────────────────────────────────────────────
def evaluate_sentiment(pred_sentiment: list, ref_sentiment: list) -> dict:
    """
    Evaluates sentiment accuracy per speaker.
    Exact match on score (positive/neutral/negative).
    """
    if not ref_sentiment:
        return {"accuracy": 0.0, "correct": 0, "total": 0, "grade": "N/A"}

    ref_map = {s["speaker"].lower(): s["score"] for s in ref_sentiment}
    pred_map = {s["speaker"].lower(): s["score"] for s in pred_sentiment}

    correct = 0
    total = len(ref_map)

    for speaker, ref_score in ref_map.items():
        pred_score = pred_map.get(speaker, "")
        if pred_score == ref_score:
            correct += 1

    accuracy = round(correct / total, 3) if total > 0 else 0.0

    return {
        "accuracy": accuracy,
        "correct": correct,
        "total": total,
        "grade": _grade(accuracy)
    }


# ── JAPAN INSIGHTS VALIDATION ─────────────────────────────────────────────────

# Deterministic nemawashi signal dictionary — does NOT rely on LLM
NEMAWASHI_KEYWORDS = {
    "そうですね", "検討します", "検討しました", "なるほど", "了解しました",
    "承知しました", "分かりました", "ご要望はよく分かりました", "素晴らしい",
    "同意します", "おっしゃる通りです", "ご指摘の通りです", "前向きに検討",
    "善処します", "検討してみます"
}

KEIGO_HIGH_MARKERS = [
    "ございます", "いただき", "おります", "申し訳", "恐れ入ります",
    "よろしくお願いいたします", "ご", "誠に"
]

KEIGO_MED_MARKERS = [
    "です", "ます", "ください", "お願いします", "ありがとう"
]


def rule_based_japan_check(transcript: str, pred_insights: dict) -> dict:
    """
    Validates Japan insights using deterministic rules — no LLM needed.
    This makes the evaluation reliable and explainable.
    """
    results = {}

    # 1. Nemawashi validation
    found_signals = [kw for kw in NEMAWASHI_KEYWORDS if kw in transcript]
    pred_signals = pred_insights.get("nemawashi_signals", [])
    detected_correctly = [s for s in pred_signals if s in found_signals]

    results["nemawashi"] = {
        "rule_detected": found_signals,
        "llm_detected": pred_signals,
        "correctly_detected": detected_correctly,
        "precision": round(len(detected_correctly) / len(pred_signals), 3) if pred_signals else 0.0,
        "recall": round(len(detected_correctly) / len(found_signals), 3) if found_signals else 1.0,
        "grade": _grade(len(detected_correctly) / max(len(found_signals), 1))
    }

    # 2. Keigo level validation
    high_count = sum(1 for m in KEIGO_HIGH_MARKERS if m in transcript)
    med_count = sum(1 for m in KEIGO_MED_MARKERS if m in transcript)

    if high_count >= 3:
        expected_keigo = "high"
    elif med_count >= 3:
        expected_keigo = "medium"
    else:
        expected_keigo = "low"

    pred_keigo = pred_insights.get("keigo_level", "unknown")
    keigo_correct = pred_keigo == expected_keigo

    results["keigo"] = {
        "rule_expected": expected_keigo,
        "llm_predicted": pred_keigo,
        "correct": keigo_correct,
        "grade": "PASS" if keigo_correct else "FAIL"
    }

    # 3. Code-switch count validation
    # Count transitions between Japanese and non-Japanese characters
    ja_pattern = re.compile(r"[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]")
    segments = re.split(r"\s+", transcript.strip())
    switches = 0
    prev_is_ja = None
    for seg in segments:
        curr_is_ja = bool(ja_pattern.search(seg))
        if prev_is_ja is not None and curr_is_ja != prev_is_ja:
            switches += 1
        prev_is_ja = curr_is_ja

    pred_switches = pred_insights.get("code_switch_count", 0)
    switch_diff = abs(pred_switches - switches)

    results["code_switching"] = {
        "rule_counted": switches,
        "llm_counted": pred_switches,
        "difference": switch_diff,
        "grade": "PASS" if switch_diff <= 3 else "FAIL"
    }

    return results


# ── MASTER EVALUATOR ──────────────────────────────────────────────────────────
def evaluate(prediction: dict, ground_truth: dict, transcript: str = "") -> dict:
    """
    Runs all evaluation metrics and returns a complete report.

    Args:
        prediction:   Output from analyze_transcript()
        ground_truth: Known correct output from test_data.py
        transcript:   Original transcript text (for rule-based checks)

    Returns:
        Full evaluation report dict
    """
    report = {}

    # Summary
    report["summary"] = evaluate_summary(
        prediction.get("summary", []),
        ground_truth.get("summary", [])
    )

    # Action items
    report["action_items"] = evaluate_action_items(
        prediction.get("action_items", []),
        ground_truth.get("action_items", [])
    )

    # Sentiment
    report["sentiment"] = evaluate_sentiment(
        prediction.get("sentiment", []),
        ground_truth.get("sentiment", [])
    )

    # Japan insights (hybrid: rule-based validation of LLM output)
    if transcript:
        report["japan_insights"] = rule_based_japan_check(
            transcript,
            prediction.get("japan_insights", {})
        )

    # Overall score
    scores = [
        report["summary"]["avg_rouge1_f1"],
        report["action_items"]["f1"],
        report["sentiment"]["accuracy"]
    ]
    report["overall_score"] = round(sum(scores) / len(scores) * 100, 1)
    report["overall_grade"] = _grade(report["overall_score"] / 100)

    return report


# ── HELPERS ───────────────────────────────────────────────────────────────────
def _grade(score: float) -> str:
    if score >= 0.8:
        return "EXCELLENT"
    elif score >= 0.6:
        return "GOOD"
    elif score >= 0.4:
        return "FAIR"
    else:
        return "POOR"


# ── QUICK TEST ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import json
    from test_data import TEST_CASES
    from analyzer import analyze_transcript

    for tc in TEST_CASES:
        print(f"\n{'='*60}")
        print(f"Running: {tc['name']} ({tc['id']})")
        print("="*60)

        prediction = analyze_transcript(tc["transcript"], tc["language"])
        report = evaluate(prediction, tc["ground_truth"], tc["transcript"])

        print(f"Overall score: {report['overall_score']}% — {report['overall_grade']}")
        print(f"Summary ROUGE-1 F1:    {report['summary']['avg_rouge1_f1']}")
        print(f"Action Items F1:       {report['action_items']['f1']}")
        print(f"Sentiment Accuracy:    {report['sentiment']['accuracy']}")
        if "japan_insights" in report:
            print(f"Keigo detection:       {report['japan_insights']['keigo']['grade']}")
            print(f"Nemawashi precision:   {report['japan_insights']['nemawashi']['precision']}")
            print(f"Code-switch diff:      {report['japan_insights']['code_switching']['difference']}")

        print(json.dumps(report, indent=2, ensure_ascii=False))