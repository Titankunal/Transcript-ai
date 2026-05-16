# Changelog

All notable changes to TranscriptAI are documented here.

Format: `[version] — date` → what changed and why.

---

## [v1.0] — 2026-05-14

**First stable release.**

### Added
- Trilingual meeting intelligence — English, Hindi, Japanese
- 16 nemawashi soft-rejection patterns with per-pattern confidence scores
- 8 Hindi indirect communication patterns (Devanagari + Roman script)
- 40+ English commitment-strength and hedging patterns
- Keigo formality detection via MeCab morphological analysis
- Cross-script speaker normalization (田中 ↔ Tanaka ↔ Director)
- APPI-compliant PII masking — names, phones, emails anonymized before LLM
- Rule-based hallucination guard — token overlap verification, no LLM self-validation
- Three-tier LLM fallback: Groq → Ollama → Mock (explicit UX feedback at each tier)
- Dynamic token budget by transcript length (prevents Ollama timeouts)
- MD5 result caching with 24-hour TTL
- JSONL observability logging with drift detection
- Meeting trends dashboard — soft rejection trends, hallucination rate, workload analysis
- Live token streaming (Groq)
- MP4/MP3/WAV/M4A transcription via Groq Whisper (free tier)
- FastAPI REST endpoints: `/analyze`, `/analyze/batch`, `/health`, `/patterns/soft-rejections`
- Async job queue via ThreadPoolExecutor
- Streamlit UI with 7 tabs and sakura/peach palette
- Deployed on Hugging Face Spaces: [KunalTheBeast/TranscriptAI](https://huggingface.co/spaces/KunalTheBeast/TranscriptAI)

### Evaluation (v1 → v4 iteration history)

| Version | Score | Primary Change |
|---|---|---|
| v1 | ~22–30% | Baseline — exact string matching, no cultural awareness |
| v2 | ~45–50% | Fuzzy names, rule-based code-switch, semantic similarity |
| v3 | ~65–75% | Cultural ground truth, JA tokenization, soft sentiment |
| v4 | ~75–85% | Hallucination guard bonus, bilingual action items, speaker fix |
| v5 | **93%** | Tone intelligence, optimal bullet assignment |

---

## [Unreleased]

Planned for future releases:

- `pyannote.audio` speaker diarization (replace silence-gap heuristic)
- Audio upload on Hugging Face Spaces (Groq Whisper API integration)
- Labeled dataset for calibrated confidence scores
- External validation on real-world transcripts
- User correction loop for fine-tuning
- Redis Queue + multi-worker FastAPI (Scale-1 path)