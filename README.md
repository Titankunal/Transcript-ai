# 🎙️ TranscriptAI — Japanese Business Intelligence

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Ollama](https://img.shields.io/badge/Ollama-qwen3%3A8b-black?style=flat-square&logoColor=white)](https://ollama.com)
[![Groq](https://img.shields.io/badge/Groq-free%20tier-orange?style=flat-square)](https://console.groq.com)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/Titankunal/Transcript-ai?style=flat-square&color=facc15)](https://github.com/Titankunal/Transcript-ai/stargazers)

**AI-powered meeting transcript analyzer optimized for Japanese business culture.**  
Extract action items, sentiment, speaker breakdowns, and Japan-specific insights.  
100% free. APPI compliant. Runs locally or in the cloud.

## 🚀 [Live Demo → transcript-ai-qkuqcld42yym54zxmyhhby.streamlit.app](https://transcript-ai-qkuqcld42yym54zxmyhhby.streamlit.app/)

</div>

---

## 📸 Screenshots

### Main Interface
![Main Interface](screenshots/main.png)

### Analysis Results — Meeting Summary
![Summary](screenshots/summary.png)

### Japan Business Intelligence Tab
![Japan Insights](screenshots/japan.png)

---

## 🤔 Why This Project?

> *"The most valuable AI projects aren't the flashy ones — they're the boring ones that solve real problems businesses have struggled with for decades."*

Every day, thousands of business meetings happen across Japanese companies. Hours of conversation get manually summarized, poorly documented, or simply forgotten. TranscriptAI solves that — but unlike a generic meeting summarizer, it understands **Japanese business culture specifically**.

### 🇯🇵 What Makes It Different

| Challenge | What it means | How TranscriptAI handles it |
|---|---|---|
| **Keigo (敬語)** | Formal honorific speech changes meaning entirely | MeCab morphological analysis detects register: high/medium/low |
| **Nemawashi (根回し)** | 検討します usually means "No" not "we'll consider it" | 16 patterns with confidence scores and cultural explanations |
| **Code-switching** | JA↔EN mixing mid-sentence in modern offices | Deterministic Unicode-range detection — not LLM estimation |
| **Speaker identity** | 田中 and Tanaka are the same person | Cross-script normalization with 100-pair Kanji↔Romaji map |
| **APPI compliance** | Japanese law — personal data cannot reach cloud LLMs | Position-based PII masking before any LLM call |

### 📈 Scales to Any Industry

| Industry | Use case |
|---|---|
| 💼 Sales / CRM | Auto-log call summaries after every client interaction |
| 🏥 Healthcare | Summarize doctor-patient consultations |
| ⚖️ Legal | Extract action items from depositions |
| 🎓 HR | Analyze interview transcripts for candidate signals |
| 💰 Finance | Flag risk signals in earnings calls |

---

## ✨ Features

- 🎙️ **Audio/Video input** — Upload MP4, MP3, WAV → Whisper transcription → analysis
- 📄 **Text input** — TXT, VTT, JSON, or paste directly
- 🌐 **Auto language detection** — Japanese, English, or mixed JA/EN
- ✅ **Action items** — owner + deadline + confidence score + hallucination flag
- 😊 **Per-speaker sentiment** — with soft cultural scoring (neutral = professional in JP)
- 📋 **Dynamic summary** — 3–8+ bullets scaled to transcript length
- 👤 **Speaker breakdown** — talk time % and tone, deduplicates cross-script identities
- 🇯🇵 **Japan insights** — keigo level, nemawashi signals, code-switch count
- 🔒 **APPI compliance** — PII masked before LLM, restored after
- 🚩 **Hallucination guard** — rule-based verification, never circular
- ⚡ **Live streaming** — see summary generate token-by-token (Groq)
- 💾 **Export as JSON** — API-ready structured output
- 📊 **Evaluation tab** — run accuracy tests against ground truth

---

## 🏗️ Architecture

```
transcription/           Input processing
  pii_masker.py          APPI compliance — mask before LLM
  speaker_normalizer.py  Resolve 田中 vs Tanaka vs (Director)
  audio_processor.py     MP4/MP3/WAV → transcript via Whisper

analysis/                Core AI pipeline
  analyzer.py            Groq → Ollama → Mock fallback
  hallucination_guard.py Rule-based claim verification (NOT LLM)
  soft_rejection_detector.py  検討します = likely No
  semantic_validator.py  sentence-transformers / TF-IDF grounding
  japanese_tokenizer.py  MeCab morphological analysis

utils/                   Infrastructure
  logger.py              JSONL observability + drift detection
  cache.py               MD5 result caching (24hr TTL)
  evaluator.py           ROUGE + semantic accuracy measurement
  japanese_names.py      500+ surname DB (JMnedict-derived)

api/                     Interfaces
  app.py                 Streamlit web UI
  api.py                 FastAPI REST (POST /analyze)
  async_processor.py     ThreadPoolExecutor job queue
```

**Critical design decisions:**
- PII restore runs **before** speaker normalization — prevents `[NAME_1]` identity confusion
- Hallucination guard is **100% rule-based** — LLM cannot grade its own output
- Code-switch counting is **rule-based Unicode detection** — LLM count ignored
- Provider is **auto** — tries Groq (3s) first, Ollama (90s), then mock with real speaker names

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com) (for local AI) **or** [Groq free key](https://console.groq.com) (for fast cloud AI)

```bash
git clone https://github.com/Titankunal/Transcript-ai.git
cd Transcript-ai
pip install -r requirements.txt

# Optional but recommended
pip install fugashi unidic-lite   # MeCab Japanese tokenizer
pip install scikit-learn           # TF-IDF semantic similarity
pip install sentence-transformers  # True semantic understanding (500MB)

# For local AI
ollama pull qwen3:8b

# Run
python -m streamlit run app.py
```

**For Groq (3s responses, free):**
```bash
export GROQ_API_KEY=your_key_here
export TRANSCRIPT_AI_PROVIDER=auto
python -m streamlit run app.py
```

---

## 🌐 REST API

```bash
pip install fastapi uvicorn
python api.py
# Docs at: http://localhost:8000/docs
```

```python
import requests
response = requests.post("http://localhost:8000/analyze", json={
    "transcript": "Tanaka: Q3の進捗を報告します。Sato: 検討いたします。",
    "language": "mixed",
    "mask_pii": True,
    "include_soft_rejections": True
})
print(response.json())
```

---

## 🔄 Swap AI Provider

One env var changes the provider. JSON schema stays identical — nothing else changes.

```bash
# Groq (recommended — free, 3s)
export GROQ_API_KEY=your_key
export TRANSCRIPT_AI_PROVIDER=auto

# Ollama only
export TRANSCRIPT_AI_PROVIDER=ollama

# Claude API
# Edit analyzer.py _call_groq() → anthropic client
```

---

## 📊 Evaluation Results

| Test Case | Score | Grade |
|---|---|---|
| Sales call (JA/EN mixed) | **75.7%** | GOOD |
| Internal meeting (Japanese heavy) | **81.6%** | GOOD |
| Client complaint call | **85.8%** | GOOD |

Started at 22–30%. Reached 75–85% through 4 systematic iterations fixing:
cultural ground truth bias, Japanese tokenization, bilingual action item matching, and hallucination prevention.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| REST API | FastAPI + Uvicorn |
| AI (cloud) | Groq + llama-3.1-8b-instant (free) |
| AI (local) | Ollama + qwen3:8b |
| Transcription | Groq Whisper / local openai-whisper |
| Japanese NLP | MeCab via fugashi + unidic-lite |
| Semantic similarity | sentence-transformers / scikit-learn TF-IDF |
| Deployment | Streamlit Community Cloud (free) |

---

## 📋 Known Limitations

| Limitation | Production Fix |
|---|---|
| Names not as speaker labels need NER for masking | spacy `ja_core_news_sm` |
| Diarization uses silence heuristics (~70% accuracy) | pyannote.audio |
| No learning loop | User feedback collection + fine-tuning |

---

## 🤝 Contributing

Pull requests welcome — especially Japanese business culture patterns, new language support, and CRM integrations.

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.

---

<div align="center">

**16 Python files · 4,654 lines · 86 functions**

Built by [Kunal Bisht](https://github.com/Titankunal)

*"Boring projects. Infinite scale."*

⭐ **Star this repo if it helped you!**

</div>