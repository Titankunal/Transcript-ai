# Contributing to TranscriptAI

Thanks for taking the time to contribute. This document covers how to set up the project locally, run tests, and submit changes.

---

## Table of Contents

- [Local Setup](#local-setup)
- [Running Tests](#running-tests)
- [Project Structure](#project-structure)
- [Submitting Changes](#submitting-changes)
- [Code Style](#code-style)
- [Reporting Issues](#reporting-issues)

---

## Local Setup

```bash
git clone https://github.com/aiKunalBisht/Transcript-ai.git
cd Transcript-ai
pip install -r requirements.txt
```

**Optional dependencies** (each unlocks a capability tier):

```bash
pip install fugashi unidic-lite       # MeCab Japanese tokenizer
pip install scikit-learn              # TF-IDF semantic similarity
pip install sentence-transformers     # Neural semantic scoring (~500MB)
pip install openai-whisper            # Local audio transcription
```

**Set your API key** (Groq is free at console.groq.com):

```bash
export GROQ_API_KEY=your_key_here
```

**Run the app:**

```bash
python -m streamlit run app.py        # Streamlit UI
python api.py                         # FastAPI REST server
```

---

## Running Tests

```bash
pip install pytest pytest-cov
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=. --cov-report=term-missing
```

Test files live in `tests/`. Each file targets a specific layer:

| File | Covers |
|---|---|
| `test_edge_1.py` | Edge cases — Japanese soft rejection detection |
| `test_edge_2.py` | Edge cases — PII masking and restoration |
| `test_edge_3.py` | Edge cases — hallucination guard |
| `test_schema_stability.py` | JSON output schema contract |

**Note on heavy dependencies:** Tests are designed to run without downloading ML models. `sentence-transformers` is optional — the system falls back to TF-IDF if not installed.

---

## Project Structure

```
Transcript-ai/
├── analyzer.py              LLM orchestration (Groq → Ollama → Mock)
├── api.py                   FastAPI REST endpoints
├── app.py                   Streamlit UI
├── async_processor.py       ThreadPoolExecutor job queue
├── audio_processor.py       Whisper transcription
├── cache.py                 MD5 result caching (24h TTL)
├── evaluator.py             ROUGE + semantic + F1 evaluation
├── hallucination_guard.py   Rule-based claim verification
├── japanese_names.py        500+ surname database
├── japanese_tokenizer.py    MeCab morphological analysis
├── language_intelligence.py Language-aware feature routing
├── logger.py                JSONL observability + trend analysis
├── meeting_store.py         Session state management
├── pii_masker.py            APPI anonymization
├── rag_retriever.py         RAG pipeline
├── semantic_validator.py    Three-tier similarity engine
├── soft_rejection_detector.py  Nemawashi + Hindi patterns
├── speaker_normalizer.py    Cross-script identity resolution
├── tests/                   All test files
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## Submitting Changes

1. Fork the repo
2. Create a branch: `git checkout -b fix/your-fix-name`
3. Make your changes
4. Run tests: `pytest tests/ -v`
5. Commit with a clear message: `git commit -m "fix: describe what changed"`
6. Push and open a Pull Request against `main`

**Commit message format:**

```
feat: add new feature
fix: fix a bug
docs: update documentation
test: add or update tests
refactor: code change with no functional impact
chore: tooling, config, CI changes
```

---

## Code Style

- Python 3.10+
- No external formatter enforced — keep it readable
- Prefer explicit over implicit
- Document public functions with a one-line docstring minimum
- Avoid print statements in production paths — use `logger.py`

---

## Reporting Issues

Open an issue at [github.com/aiKunalBisht/Transcript-ai/issues](https://github.com/aiKunalBisht/Transcript-ai/issues).

Include:
- What you expected to happen
- What actually happened
- Transcript language (EN / HI / JA)
- Provider used (Groq / Ollama / Mock)
- Python version and OS