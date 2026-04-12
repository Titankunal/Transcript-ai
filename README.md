<div align="center">

# TranscriptAI · 文字起こし分析エンジン

**Enterprise-grade meeting intelligence for the Japanese business market**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-REST%20API-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-Web%20UI-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/Groq-Free%20Tier-F55036?style=flat-square)](https://console.groq.com)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black?style=flat-square)](https://ollama.com)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)
[![Stars](https://img.shields.io/github/stars/Titankunal/Transcript-ai?style=flat-square&color=facc15)](https://github.com/Titankunal/Transcript-ai/stargazers)

**[Live Demo](https://transcript-ai-qkuqcld42yym54zxmyhhby.streamlit.app) · [API Docs](https://transcript-ai-qkuqcld42yym54zxmyhhby.streamlit.app) · [GitHub](https://github.com/Titankunal/Transcript-ai)**

</div>

---

## Overview

TranscriptAI is a production-grade AI system that converts meeting recordings and transcripts into structured business intelligence. It is purpose-built for the Japanese enterprise market — handling the linguistic and cultural nuances that generic tools miss entirely.

Japanese business communication is fundamentally different from English. A speaker saying **検討します** (we will consider it) almost never means they will consider it. **難しいかもしれません** (it may be difficult) is a polite rejection, not an assessment of difficulty. **前向きに検討** (positive consideration) signals uncertainty, not optimism. TranscriptAI reads these signals and surfaces them explicitly, so decision-makers see what was actually communicated — not what was literally said.

The system is deployed live, free to use, and built on a fully swappable LLM architecture. Groq (3-second cloud inference), Ollama (local, APPI-compliant), and any OpenAI-compatible provider can be switched with a single environment variable.

---

## The Japanese Intelligence Layer

This is the core differentiator. Every feature below addresses a real gap in existing tools.

### Keigo Register Detection · 敬語レベル検出

Japanese has three honorific registers — teineigo (polite), sonkeigo (respectful), and kenjougo (humble) — that fundamentally change the meaning and power dynamic of a conversation. TranscriptAI uses MeCab morphological analysis to classify register at the utterance level, not just keyword frequency.

Output: `high` / `medium` / `low` register label with MeCab as the authoritative source, overriding LLM classification which confuses medium and high registers in 40% of cases.

### Nemawashi Signal Detection · 根回し検出

Sixteen indirect rejection and hesitation patterns with severity levels, confidence scores, speaker attribution, and cultural explanations.

| Severity | Pattern | Reading | Confidence | True Intent |
|---|---|---|---|---|
| 🔴 HIGH | 難しいかもしれません | It may be difficult | 90% | Rejection |
| 🔴 HIGH | 対応しかねます | Unable to accommodate | 95% | Rejection |
| 🟡 MEDIUM | 検討します / 検討いたします | We will consider it | 72% | Likely No |
| 🟡 MEDIUM | 前向きに検討 | Positive consideration | 55% | Uncertain |
| 🟡 MEDIUM | 善処します | Will handle appropriately | 68% | Likely No |
| 🟡 MEDIUM | 上司に相談 | Will consult superior | 50% | Deferral |
| 🟢 LOW | 懸念がございます | There are concerns | 45% | Hesitation |
| 🟢 LOW | そうですね | I see / That's right | 25% | Ambiguous |

Each detected signal includes the surrounding transcript context with `【phrase】` highlighting so reviewers can verify in context.

### Code-Switch Counter · 言語切替検出

Counts JA↔EN language transitions using Unicode range detection — not LLM estimation, which was off by 7–15 switches in testing. The rule-based count is authoritative. Timestamps and speaker labels are stripped before counting to prevent false positives.

### Cross-Script Speaker Normalization

田中 and Tanaka are the same person. `Tanaka (Director):` and `田中:` in the same transcript refer to the same speaker. The normalizer handles:

- Role suffix stripping: `Tanaka (Director)` → `Tanaka`
- Kanji↔Romaji mapping: 100-pair dictionary covering top surnames by population frequency
- Orphaned parentheses: `Dev)` → resolved correctly
- Japanese honorific stripping: `田中部長` → `田中`
- Deduplication: merges talk-time percentages across matched identities

---

## APPI Compliance · 個人情報保護法対応

Japan's Act on the Protection of Personal Information (APPI) prohibits sending personally identifiable information to external LLM providers without explicit consent. TranscriptAI solves this with a local anonymization pipeline.

**Before any data reaches an LLM:**

| Category | Detection method | Example |
|---|---|---|
| Speaker names (Latin) | Position-based — any word before `:` in a speaker label | `Tanaka:` → `[NAME_1]:` |
| Speaker names (CJK) | CJK character pattern before `：` | `田中:` → `[NAME_2]:` |
| Japanese surnames | 500+ entry database (JMnedict-derived, ~95% population coverage) | `鈴木` → `[NAME_3]` |
| Email addresses | RFC 5322 pattern | `a@b.co.jp` → `[EMAIL_1]` |
| Phone numbers (JP) | +81 and 0X formats | `090-1234-5678` → `[PHONE_1]` |
| Phone numbers (intl) | +country code format | `+1-555-0100` → `[PHONE_1]` |
| Companies (JP) | 株式会社 / 有限会社 / 合同会社 prefix | `株式会社テクノ` → `[COMPANY_1]` |
| Companies (EN) | Inc / Ltd / LLC / Corp suffix | `Acme Corp` → `[COMPANY_1]` |

After LLM processing, real values are restored locally before any result is displayed. The LLM only ever processes anonymized text.

**Documented limitation:** Names that do not appear as speaker labels and are not in the surname database require a production NER model (e.g. spaCy `ja_core_news_sm`) for full coverage. This is the honest state of the system and is surfaced to users.

---

## Analysis Pipeline

**Input formats:** TXT, VTT, JSON (paste or upload) · MP4, MP3, WAV, M4A (Whisper transcription)

**Output — structured JSON with guaranteed schema:**

```json
{
  "summary": ["bullet 1", "bullet 2", "...scaled to transcript length"],
  "action_items": [
    {
      "task": "Prepare security audit report",
      "owner": "Priya",
      "deadline": "Friday EOD",
      "confidence": 0.95,
      "hallucination_flag": false
    }
  ],
  "sentiment": [
    { "speaker": "Tanaka", "score": "neutral", "label": "Professional formal register" }
  ],
  "speakers": [
    { "name": "Tanaka", "talk_time_pct": 42, "tone": "formal" }
  ],
  "japan_insights": {
    "keigo_level": "high",
    "keigo_source": "mecab",
    "nemawashi_signals": ["検討いたします", "難しいかもしれません"],
    "code_switch_count": 19,
    "code_switch_source": "rule_based"
  },
  "soft_rejections": {
    "risk_level": "HIGH",
    "risk_summary": "Multiple rejection signals detected.",
    "detected": [...]
  },
  "verification": {
    "overall_hallucination_risk": 0.077,
    "risk_label": "LOW"
  }
}
```

**Summary length scales with transcript:** 3 bullets (<200 words) · 5 bullets (<600 words) · 7 bullets (<1,200 words) · 8+ bullets (full meetings)

---

## Hallucination Prevention

The guard verifies every claim in the output against the original transcript. It is **100% rule-based** — the LLM never validates its own output, which would be circular.

**Verification formula:**

```
effective_score = max(token_overlap_score, tf_idf_cosine_score)

token_overlap  = |claim_tokens ∩ transcript_tokens| / |claim_tokens|
tf_idf_cosine  = cosine_similarity(TF-IDF vectors)  [cross-language aware]
```

Items with `effective_score < 0.20` are flagged with a confidence percentage and a specific reason. Items rescued by the semantic layer are marked `rescued_by: semantic_validation`.

**Semantic validation tiers** (best available is used automatically):

1. **sentence-transformers** · `paraphrase-multilingual-MiniLM-L12-v2` · true meaning, Japanese+English native · `pip install sentence-transformers`
2. **scikit-learn TF-IDF** · keyword weighting with EN→JA bridge dictionary · `pip install scikit-learn`
3. **Pure Python** · token overlap · always available, no install required

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  transcription/                                                 │
│    pii_masker.py          APPI anonymization pipeline           │
│    speaker_normalizer.py  Cross-script identity resolution      │
│    audio_processor.py     Whisper transcription (Groq / local)  │
├─────────────────────────────────────────────────────────────────┤
│  analysis/                                                      │
│    analyzer.py            LLM orchestration + fallback          │
│    hallucination_guard.py Rule-based claim verification         │
│    soft_rejection.py      16-pattern nemawashi detector         │
│    semantic_validator.py  Three-tier similarity engine          │
│    japanese_tokenizer.py  MeCab morphological analysis          │
├─────────────────────────────────────────────────────────────────┤
│  utils/                                                         │
│    logger.py              JSONL observability + drift detection │
│    cache.py               MD5 result caching (24hr TTL)         │
│    evaluator.py           ROUGE + semantic accuracy             │
│    japanese_names.py      500+ surname DB (JMnedict-derived)    │
├─────────────────────────────────────────────────────────────────┤
│  api/                                                           │
│    app.py                 Streamlit web UI                      │
│    api.py                 FastAPI REST endpoints                │
│    async_processor.py     ThreadPoolExecutor job queue          │
└─────────────────────────────────────────────────────────────────┘
```

**Critical design decisions:**

- PII restore runs before speaker normalization — normalizer would otherwise receive `[NAME_1]` instead of `Tanaka`
- Code-switch count is deterministic (Unicode ranges) — LLM count is discarded
- Keigo classification from MeCab overrides LLM output — LLM confused registers in 40% of test cases
- Provider `auto` mode: Groq success → return immediately, never fall through to Ollama
- Ollama timeout: 90 seconds, zero retries — if slow once, it will be slow again

---

## LLM Provider Configuration

```
TRANSCRIPT_AI_PROVIDER=auto   # Groq (3s) → Ollama (90s) → Mock
TRANSCRIPT_AI_PROVIDER=groq   # Groq only
TRANSCRIPT_AI_PROVIDER=ollama # Ollama only
```

Both providers use `response_format: json_object` / `format: json` for guaranteed schema compliance at the API level. The JSON schema is identical regardless of provider — swapping is one environment variable.

| Provider | Latency | Cost | APPI | Requirements |
|---|---|---|---|---|
| Groq (llama-3.1-8b-instant) | ~3s | Free (500 req/day) | ✅ with PII masking | `GROQ_API_KEY` |
| Ollama (qwen3:8b) | ~60–90s | Free (local) | ✅ fully local | Ollama running |
| Mock | Instant | Free | N/A | None — demo only |

---

## Evaluation

Custom evaluation system with bilingual ground truth across three test cases.

**Metrics:** Semantic similarity (ROUGE-1 + ROUGE-2 + LCS), Action item F1 (bilingual EN/JA), Sentiment accuracy with soft cultural scoring, Japan insights (keigo PASS/PARTIAL/FAIL, nemawashi precision, code-switch authoritative).

**Cultural correction:** Standard NLP evaluation labeled Japanese professional neutral speech as "positive" — a Western bias. Ground truth was corrected: neutral IS the professional standard in Japanese business communication. Soft scoring gives 0.5 credit for culturally valid alternatives.

| Test case | v1 (baseline) | v4 (current) | Change |
|---|---|---|---|
| Sales call · JA/EN mixed | 30.8% | **75.7% GOOD** | +44.9% |
| Internal meeting · Japanese heavy | 22.2% | **81.6% GOOD** | +59.4% |
| Client complaint · tense | 55.9% | **85.8% GOOD** | +29.9% |

Each iteration was driven by what the evaluation system revealed — not guesswork. v1 had hard exact matching. v2 added fuzzy names and rule-based code-switching. v3 corrected cultural ground truth and added JA tokenization. v4 added hallucination guard bonus and bilingual action item matching.

---

## REST API

```bash
pip install fastapi uvicorn
python api.py
# Interactive docs: http://localhost:8000/docs
```

**Endpoints:**

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Status, available modules, provider |
| `POST` | `/analyze` | Single transcript analysis |
| `POST` | `/analyze/batch` | Up to 10 transcripts concurrently |
| `GET` | `/patterns/soft-rejections` | Full nemawashi pattern dictionary |

**Example:**

```python
import requests

response = requests.post("http://localhost:8000/analyze", json={
    "transcript": "Tanaka: Q3の進捗を報告します。検討いたします。難しいかもしれません。",
    "language": "mixed",
    "mask_pii": True,
    "include_soft_rejections": True
})

result = response.json()
print(result["result"]["soft_rejections"]["risk_level"])   # HIGH
print(result["result"]["japan_insights"]["keigo_level"])   # high
```

---

## Installation

```bash
git clone https://github.com/Titankunal/Transcript-ai.git
cd Transcript-ai
pip install -r requirements.txt
```

**Optional dependencies** (each unlocks a capability tier):

```bash
pip install fugashi unidic-lite        # MeCab Japanese tokenizer
pip install scikit-learn               # TF-IDF semantic similarity
pip install sentence-transformers      # True semantic understanding (~500MB model)
pip install openai-whisper             # Local audio transcription
```

**Run with Groq** (recommended — free, 3-second responses):

```bash
export GROQ_API_KEY=your_key_here     # get free at console.groq.com
python -m streamlit run app.py
```

**Run with Ollama** (fully local, APPI-compliant, no API key):

```bash
ollama pull qwen3:8b
python -m streamlit run app.py
```

---

## Scaling

The current architecture handles concurrent requests via `ThreadPoolExecutor`. For higher throughput:

```
Current:    ThreadPoolExecutor (3 workers) + FastAPI async endpoints
Scale-1:    Redis Queue (RQ) as job broker + multiple FastAPI worker processes
Scale-2:    vLLM for high-throughput batched LLM inference
Scale-3:    Kubernetes deployment with horizontal pod autoscaling
```

The JSON schema contract is the stable interface at every scale level. Downstream CRM integrations, dashboards, and HR systems do not change when the infrastructure scales.

---

## Codebase

| Metric | Value |
|---|---|
| Python files | 16 |
| Lines of code | 4,654 |
| Functions | 86 |
| Test cases (ground truth) | 3 bilingual |
| Nemawashi patterns | 16 |
| Japanese surname database | 500+ entries |
| Kanji↔Romaji mappings | 100 pairs |
| Supported input formats | TXT · VTT · JSON · MP4 · MP3 · WAV · M4A |

---

## Known Limitations

| Limitation | Current behavior | Production path |
|---|---|---|
| Names not as speaker labels and not in surname DB | Not masked | spaCy `ja_core_news_sm` NER |
| Speaker diarization (audio input) | Silence-gap heuristic (~70%) | pyannote.audio |
| Semantic similarity without sentence-transformers | TF-IDF keyword weighting | `pip install sentence-transformers` |
| No learning loop | System does not improve from feedback | User feedback collection + fine-tuning |

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

<div align="center">

Built by [Kunal Bisht](https://github.com/Titankunal) · Meerut, India

*Boring problems. Production engineering. Infinite scale.*

</div>