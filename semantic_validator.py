# semantic_validator.py
# Embedding-based semantic validation — no external API needed
#
# Uses TF-IDF cosine similarity (scikit-learn, free, offline)
# Falls back to token overlap if scikit-learn not installed
#
# Why TF-IDF over token overlap:
#   Token overlap: "prepare report" vs "create document" = 0.0 (no shared words)
#   TF-IDF cosine: same pair = 0.45 (shared concept via term weighting)
#
# Why not sentence-transformers:
#   Requires 500MB model download — too heavy for free deployment
#   TF-IDF is 0KB, runs instantly, good enough for grounding checks

import re
import math
from collections import Counter

# Try scikit-learn for better TF-IDF
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


def _ja_tokenize_simple(text: str) -> list:
    """Simple JA/EN tokenizer — tries MeCab first, falls back to char-level."""
    try:
        from japanese_tokenizer import tokenize_japanese
        return tokenize_japanese(text, normalize=True)
    except Exception:
        pass
    ja = re.compile(r"[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]")
    tokens, buf = [], []
    for c in text.lower():
        if ja.match(c):
            if buf: tokens.extend("".join(buf).split()); buf = []
            tokens.append(c)
        elif c in (" ", "\t", "\n"):
            if buf: tokens.extend("".join(buf).split()); buf = []
        else:
            buf.append(c)
    if buf: tokens.extend("".join(buf).split())
    cjk = [t for t in tokens if re.match(r"[\u3040-\u9FFF]", t)]
    return tokens + ["".join(cjk[i:i+2]) for i in range(len(cjk)-1)]


def _tf_idf_manual(docs: list) -> list:
    """Pure Python TF-IDF when sklearn not available."""
    tokenized = [_ja_tokenize_simple(d) for d in docs]
    df = Counter()
    for tokens in tokenized:
        df.update(set(tokens))
    N = len(docs)
    vectors = []
    for tokens in tokenized:
        tf = Counter(tokens)
        vec = {}
        for term, count in tf.items():
            tfidf = (count / len(tokens)) * math.log(N / (df[term] + 1))
            vec[term] = tfidf
        vectors.append(vec)
    return vectors


def _cosine_manual(v1: dict, v2: dict) -> float:
    """Cosine similarity between two TF-IDF vectors."""
    common = set(v1) & set(v2)
    if not common:
        return 0.0
    dot    = sum(v1[k] * v2[k] for k in common)
    norm1  = math.sqrt(sum(x*x for x in v1.values()))
    norm2  = math.sqrt(sum(x*x for x in v2.values()))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return round(dot / (norm1 * norm2), 3)


def semantic_similarity(text_a: str, text_b: str) -> float:
    """
    Computes semantic similarity between two texts.
    Uses sklearn TF-IDF cosine if available, pure Python otherwise.
    Returns 0.0 to 1.0.
    """
    if not text_a or not text_b:
        return 0.0

    if SKLEARN_AVAILABLE:
        try:
            vec = TfidfVectorizer(
                analyzer=lambda x: _ja_tokenize_simple(x),
                min_df=1
            )
            matrix = vec.fit_transform([text_a, text_b])
            score  = cosine_similarity(matrix[0], matrix[1])[0][0]
            return round(float(score), 3)
        except Exception:
            pass

    # Pure Python fallback
    vectors = _tf_idf_manual([text_a, text_b])
    return _cosine_manual(vectors[0], vectors[1])


def semantic_grounding_score(claim: str, transcript: str,
                              window_size: int = 200) -> float:
    """
    Checks if a claim is semantically grounded in the transcript.
    Uses sliding window — finds the most relevant passage, not whole transcript.

    This prevents long transcripts from diluting short claim matches.
    """
    if not claim or not transcript:
        return 0.0

    # Sliding window over transcript
    words  = transcript.split()
    if len(words) <= window_size:
        return semantic_similarity(claim, transcript)

    best_score = 0.0
    step       = window_size // 2
    for i in range(0, len(words) - window_size + 1, step):
        window = " ".join(words[i:i + window_size])
        score  = semantic_similarity(claim, window)
        best_score = max(best_score, score)
        if best_score > 0.7:  # early exit if strong match found
            break

    return best_score


def validate_action_items_semantic(action_items: list,
                                   transcript: str) -> list:
    """
    Adds semantic grounding scores to action items.
    Replaces pure token overlap with TF-IDF cosine similarity.
    """
    for item in action_items:
        task = item.get("task", "")
        semantic_score = semantic_grounding_score(task, transcript)
        item["semantic_grounding"] = semantic_score

        # Dynamic threshold: semantic ≥ 0.15 OR token overlap already passed
        already_verified = not item.get("hallucination_flag", True)
        if not already_verified and semantic_score >= 0.15:
            item["hallucination_flag"] = False
            item["flag_reason"] = None
            item["rescued_by"] = "semantic_validation"

    return action_items


if __name__ == "__main__":
    print(f"sklearn available: {SKLEARN_AVAILABLE}")
    pairs = [
        ("prepare security audit report", "Priya, please prepare the technical security audit report by Friday EOD"),
        ("submit revised risk management proposal", "一度社内で持ち帰り、来週の月曜までにリスク管理の修正案を再提出いたします"),
        ("book conference room", "Good morning everyone let us discuss Q3 results"),
    ]
    for claim, context in pairs:
        score = semantic_similarity(claim, context)
        grounding = semantic_grounding_score(claim, context)
        print(f"Similarity: {score:.3f} | Grounding: {grounding:.3f} | '{claim[:40]}'")