---
title: TranscriptAI
emoji: 🎙️
colorFrom: pink
colorTo: yellow
sdk: streamlit
sdk_version: 1.55.0
app_file: app.py
pinned: true
license: mit
short_description: Speech & Meeting Intelligence — English · Hindi · Japanese
---

<div align="center">

# 🎙️ TranscriptAI

### Speech & Meeting Intelligence Platform

<p>
  <a href="https://huggingface.co/spaces/KunalTheBeast/TranscriptAI">
    <img src="https://img.shields.io/badge/🚀%20Live%20Demo-HuggingFace-D96080?style=for-the-badge" alt="Live Demo"/>
  </a>
  &nbsp;
  <a href="https://github.com/aiKunalBisht/Transcript-ai">
    <img src="https://img.shields.io/badge/GitHub-Source%20Code-3C2416?style=for-the-badge&logo=github" alt="GitHub"/>
  </a>
</p>

<p>
  <img src="https://img.shields.io/badge/Python-3.10%2B-C45C74?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Streamlit-UI-D96080?style=flat-square&logo=streamlit&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-REST%20API-486858?style=flat-square&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/Groq-Free%20Tier-B87830?style=flat-square"/>
  <img src="https://img.shields.io/badge/Eval%20Score-93%25%20EXCELLENT-486858?style=flat-square"/>
  <img src="https://img.shields.io/badge/License-MIT-A8897C?style=flat-square"/>
</p>

<br/>

**Turn any meeting or speech into structured intelligence.**
Summaries · Action Items · Tone Analysis · Communication Risk Signals

*Works in English, Hindi, and Japanese — output always in English.*

</div>

---

## What It Does

Paste or upload any transcript and get structured intelligence in seconds.

```
Input:  "Rahul: Vikram, client report Monday tak ready honi chahiye."
        "Vikram: Dekhte hain. Thoda mushkil hai."

Output: ✅ Action Item  → Prepare client report | Owner: Vikram | Deadline: Monday
        🔴 Hindi Signal → "dekhte hain"       — Classic Indian soft no (80% confidence)
        🔴 Hindi Signal → "thoda mushkil hai" — Indirect refusal (85% confidence)
        ⚠️  Risk Level  → HIGH — Commitment unlikely to be followed through
        🟣 Tone         → Hesitant / Uncertain (Intensity: 2/5)
```

---

## The Core Idea

Most meeting tools extract *what* was said. TranscriptAI extracts *how* people communicate.

Each language has its own indirect communication patterns. A generic summarizer misses all of them:

| What was said | Generic AI | TranscriptAI |
|---|---|---|
| *"Dekhte hain"* | "We will see" — neutral | 🔴 Classic Indian soft no — unlikely to happen |
| *"検討いたします"* | "We will consider it" — action item | ⚠️ 72% rejection confidence — follow up in writing |
| *"We'll circle back"* | Meeting note | 🌀 Corporate hedging — no concrete next step |
| *"Haan haan bilkul"* | "Yes absolutely" — agreement | 🟠 Hierarchical yes — agreeing to please, may not follow through |

---

## Language Intelligence Layers

Three separate NLP engines, auto-detected from the transcript:

### 🇮🇳 Hindi / Hinglish
- Indirect no — `dekhte hain`, `thoda mushkil hai`, `koshish karenge`
- Hierarchical yes — `haan haan bilkul`, `jo aap kahenge`
- Face-saving exits — `upar se baat karta hoon`
- Jugaad framing — `kuch na kuch ho jayega`
- Respect deflection — `aap jo theek samjhe`
- Detects both **Roman script and Devanagari**

### 🇬🇧 English
- Commitment strength meter — "I will" vs "I'll try" vs "we'll see"
- Escalation signals — "going to have to escalate", "reconsider the contract"
- Power imbalance — "this is unacceptable", "you need to understand"
- Corporate hedging — "circle back", "take under advisement", "touch base"
- Passive aggression — "fine", "whatever works for you"
- 40+ patterns across 4 categories

### 🇯🇵 Japanese
- 16 nemawashi soft rejection patterns with confidence scores
- Keigo formality detection via MeCab morphological analysis
- Deterministic JA↔EN code-switch counting
- Cross-script speaker normalization — 田中 and Tanaka are the same speaker

---

## Features

**Summary Tab**
- Full narrative paragraph — what was discussed, decided, and the outcome
- 3–8 key bullet points scaled to transcript length
- Previous session panel — meeting continuity tracking

**Meeting Health Score** — 0–100 from 4 signals

```
Sentiment (30) + Action Clarity (25) + Communication Risk (25) + AI Confidence (20)
```

| Score | Label |
|---|---|
| 80–100 | 🟢 Productive Meeting |
| 60–79 | 🟡 Mostly Aligned |
| 40–59 | 🟠 Needs Follow-up |
| 0–39 | 🔴 High Risk |

**Speaker Tone Intelligence** — 6-level color-coded scale with intensity bars 1–5

```
🔴 Aggressive → 🟠 Assertive → 🟡 Neutral → 🟢 Cooperative → 🔵 Deferential → 🟣 Hesitant
```

**Production Features**
- APPI-compliant PII masking — names, phones, emails anonymized before LLM; restored after
- Hallucination guard — 100% rule-based token overlap, LLM never validates itself
- Groq → Ollama → Mock fallback with explicit UX feedback per provider
- Meeting trends dashboard — soft rejection trends, hallucination drift, workload
- FastAPI REST endpoint for CRM integration
- MD5 result caching (24h TTL) + JSONL observability logging

---

## Evaluation — 93% Overall Score

Custom evaluation system with **cultural corrections** — standard NLP metrics have Western bias.
Japanese professional neutral speech is NOT incorrect. Soft sentiment scoring applied.

| Version | Score | Key change |
|---|---|---|
| v1 | 30% | Baseline — exact matching only |
| v2 | 55% | Fuzzy names, rule-based code-switch, semantic similarity |
| v3 | 75% | Cultural ground truth, JA tokenization, soft sentiment |
| v4 | 83% | Hallucination guard, nemawashi filter, speaker sort |
| **v5** | **93% EXCELLENT** | Sentiment rules, tone intelligence, optimal bullet matching |

| Metric | Score |
|---|---|
| Action Items F1 | 1.0 — EXCELLENT |
| Sentiment (soft/cultural) | 1.0 — EXCELLENT |
| Hallucination Risk | LOW |
| **Overall** | **93% — EXCELLENT** |

---

## Architecture

```
transcription/
  pii_masker.py          APPI anonymization — before LLM (v3: handles all bracket variants)
  speaker_normalizer.py  Cross-script identity resolution
  audio_processor.py     Whisper transcription

analysis/
  analyzer.py            Groq → Ollama → Mock · trilingual detection · tone schema
  english_analyzer.py    English NLP — 40+ patterns (hedging, power, escalation)
  hindi_analyzer.py      Hindi NLP — 30+ patterns (Roman + Devanagari)
  soft_rejection.py      Japanese 16-pattern nemawashi detector
  hallucination_guard.py 100% rule-based claim verification
  japanese_tokenizer.py  MeCab morphological analysis

utils/
  evaluator.py           ROUGE + semantic + F1 + optimal assignment matching
  logger.py              JSONL logging + trend analysis engine
  cache.py               MD5 result caching

app.py                   Streamlit UI — translucent navbar, 7 tabs, health score
api.py                   FastAPI REST endpoints
```

**Processing order (sequence is critical):**
```
1. PII mask       — local, before LLM         (APPI compliance)
2. LLM analysis   — Groq / Ollama / Mock
3. PII restore    — local, before normalization (so normalizer sees real names)
4. Normalize      — cross-script speaker dedup
5. Tone classify  — 6-level scale per speaker
6. NLP layer      — language-specific routing
7. Cache + log    — local JSONL
```

---

## Quick Start

```bash
git clone https://github.com/aiKunalBisht/Transcript-ai.git
cd Transcript-ai
pip install -r requirements.txt

# Recommended — Groq (1-2 second analysis, free tier)
export GROQ_API_KEY=your_key_here    # free at console.groq.com
python -m streamlit run app.py

# Fully local — zero data leaves your machine
ollama pull qwen3:8b
python -m streamlit run app.py
```

Optional:
```bash
pip install fugashi unidic-lite      # MeCab Japanese tokenizer
pip install scikit-learn             # TF-IDF semantic similarity
pip install sentence-transformers    # Neural semantic understanding (~500MB)
```

---

## REST API

```bash
python api.py
# Interactive docs: http://localhost:8000/docs
```

```python
import requests

r = requests.post("http://localhost:8000/analyze", json={
    "transcript": "Rahul: Friday tak deliver ho sakta hai? Priya: Dekhte hain.",
    "language": "hi",
    "mask_pii": True
})
print(r.json()["result"]["soft_rejections"]["risk_level"])   # HIGH
print(r.json()["result"]["soft_rejections"]["risk_summary"]) # Commitment unlikely...
```

---

## Known Limitations

| Limitation | Path Forward |
|---|---|
| Speaker diarization ~70% accuracy | pyannote.audio |
| Audio unavailable on HF Spaces | Groq Whisper API (next) |
| 3 synthetic test cases | External validation on real transcripts |
| Confidence scores are heuristic | Labeled dataset + calibration |
| No feedback loop | User correction collection + fine-tuning |

---

## Numbers

```
19 Python files  ·  6,000+ lines  ·  90+ functions
40+ English patterns  ·  30+ Hindi patterns  ·  16 Japanese soft rejection patterns
500+ Japanese surnames  ·  Eval score: 93% EXCELLENT
Formats: TXT · VTT · JSON · MP4 · MP3 · WAV · M4A
```

---

<div align="center">

Built by **[Kunal Bisht](https://github.com/aiKunalBisht)** · Pithoragarh, Uttarakhand, India

[LinkedIn](https://linkedin.com/in/kunalhere) &nbsp;·&nbsp; [Hugging Face](https://huggingface.co/KunalTheBeast)

</div>