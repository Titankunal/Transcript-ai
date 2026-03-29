# 🎙️ TranscriptAI — Japanese Business Intelligence

<div align="center">

![TranscriptAI Banner](https://img.shields.io/badge/TranscriptAI-Japanese%20Business%20Intelligence-6C63FF?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAxYy02LjYgMC0xMiA1LjQtMTIgMTJzNS40IDEyIDEyIDEyIDEyLTUuNCAxMi0xMlMxOC42IDEgMTIgMXptMCAyMmMtNS41IDAtMTAtNC41LTEwLTEwUzYuNSAyIDEyIDJzMTAgNC41IDEwIDEwLTQuNSAxMC0xMCAxMHoiLz48L3N2Zz4=)

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Ollama](https://img.shields.io/badge/Ollama-qwen3%3A8b-black?style=flat-square&logo=ollama&logoColor=white)](https://ollama.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/Titankunal/Transcript-ai?style=flat-square&color=yellow)](https://github.com/Titankunal/Transcript-ai/stargazers)

**AI-powered meeting transcript analyzer optimized for Japanese business culture.**
Extract action items, sentiment, speaker breakdowns, and Japan-specific insights — 100% free, runs locally.

[🚀 Live Demo](#demo) · [📖 Docs](#installation) · [🗺️ Roadmap](#roadmap) · [⭐ Star this repo](#)

</div>

---

## 📸 Screenshots

| Main Interface | Analysis Results | Japan Insights |
|---|---|---|
| ![Main UI](https://via.placeholder.com/400x250/1a1a2e/6C63FF?text=Transcript+Input+UI) | ![Results](https://via.placeholder.com/400x250/1a1a2e/6C63FF?text=Analysis+Results) | ![Japan](https://via.placeholder.com/400x250/1a1a2e/6C63FF?text=Japan+Insights+Tab) |

> 💡 **Replace these placeholders** with real screenshots from your running app!

---

## 🎬 Demo

<div align="center">

![Demo GIF](https://via.placeholder.com/800x450/1a1a2e/6C63FF?text=Demo+GIF+—+Record+with+ScreenToGif+or+OBS)

> 🎥 Record a demo GIF using [ScreenToGif](https://www.screentogif.com/) (free) and replace this placeholder.

</div>

---

## 🤔 Why This Project?

> *"The most valuable AI projects aren't the flashy ones — they're the boring ones that solve real problems businesses have struggled with for decades."*

Every day, thousands of business meetings happen across Japanese companies. Sales calls, client check-ins, internal standups — all generating hours of conversation that get **manually summarized, poorly documented, or simply forgotten.**

This project solves that with AI. But here's what makes it different from a generic meeting summarizer:

### 🇯🇵 The Japanese Business Culture Problem

Japanese business communication is uniquely challenging for AI:

| Challenge | What it means | How TranscriptAI handles it |
|---|---|---|
| **Keigo (敬語)** | Formal honorific speech changes meaning | Detects register level: high/medium/low |
| **Nemawashi (根回し)** | Indirect consensus-building disguised as agreement | Extracts phrases like そうですね, 検討します |
| **Code-switching** | JA↔EN mixing mid-sentence in modern offices | Counts switches, handles bilingual context |
| **Indirect refusal** | "We will consider it" often means "No" | Flags ambiguous sentiment per speaker |

### 📈 Why It's Scalable

This isn't a toy. The same architecture scales directly into:
- **CRM systems** → auto-log call summaries after every sales call
- **HR platforms** → analyze interview transcripts for candidate sentiment
- **Healthcare** → summarize doctor-patient consultations
- **Legal** → extract action items from deposition transcripts
- **Finance** → flag risk signals in earnings call transcripts

One JSON schema. Infinite industries.

---

## ✨ Features

- 📄 **Multi-format input** — Upload `.txt`, `.vtt`, `.json` or paste directly
- 🌐 **Auto language detection** — Japanese, English, or mixed JA/EN
- ✅ **Action item extraction** — Owner + deadline pulled from conversation
- 😊 **Per-speaker sentiment** — Positive / Neutral / Negative with reasoning
- 📋 **Meeting summary** — 3-5 bullet TL;DR
- 👤 **Speaker breakdown** — Talk time % and tone per participant
- 🇯🇵 **Japan insights** — Keigo level, nemawashi signals, code-switch count
- 💾 **Export as JSON** — Feed into any downstream system
- 🕐 **Analysis history** — Last 5 analyses saved in sidebar
- 🔒 **100% local** — Your data never leaves your machine

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    STREAMLIT UI                         │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ File Upload │  │  Paste Text  │  │ Language Sel. │  │
│  └──────┬──────┘  └──────┬───────┘  └───────┬───────┘  │
└─────────┼────────────────┼──────────────────┼──────────┘
          └────────────────┼──────────────────┘
                           ▼
              ┌────────────────────────┐
              │   Language Detection   │
              │   (langdetect)         │
              │   JA / EN / Mixed      │
              └───────────┬────────────┘
                          ▼
              ┌────────────────────────┐
              │   LLM Core             │
              │   Ollama + qwen3:8b    │
              │   Structured JSON out  │
              └───────────┬────────────┘
                          ▼
        ┌─────────────────────────────────────┐
        │           OUTPUT PIPELINE           │
        │                                     │
        │  ✅ Action Items  😊 Sentiment      │
        │  📋 Summary       👤 Speakers       │
        │                                     │
        └─────────────────┬───────────────────┘
                          ▼
        ┌─────────────────────────────────────┐
        │     🇯🇵 JAPAN INTELLIGENCE LAYER    │
        │                                     │
        │  敬語 Keigo Detector                │
        │  根回し Nemawashi Signal Extractor  │
        │  JA↔EN Code-Switch Handler          │
        │                                     │
        └─────────────────────────────────────┘
```

---

## 🚀 Installation

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com) installed

### 1. Clone the repo
```bash
git clone https://github.com/Titankunal/Transcript-ai.git
cd Transcript-ai
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Pull the AI model
```bash
ollama pull qwen3:8b
```

### 4. Run the app
```bash
python -m streamlit run app.py
```

Open **http://localhost:8501** 🎉

---

## 🔄 Swapping the AI Provider

The `analyzer.py` file is designed for easy provider swaps. The JSON schema stays identical — nothing else in the app changes.

**→ Claude (Anthropic)**
```python
import anthropic
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
message = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": build_prompt(text, language)}]
)
return json.loads(message.content[0].text)
```

**→ Gemini (Google — free tier)**
```python
import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content(build_prompt(text, language))
return json.loads(response.text)
```

Store your key in `.streamlit/secrets.toml`:
```toml
ANTHROPIC_API_KEY = "your_key_here"
```

---

## 🗺️ Roadmap

### ✅ v1.0 — Current
- [x] Core transcript analysis pipeline
- [x] Japan-specific intelligence layer
- [x] Streamlit UI with tabbed results
- [x] Local LLM via Ollama (free, private)
- [x] JSON export

### 🔨 v1.1 — Coming Soon
- [ ] Audio file input (`.mp3`, `.wav`) with Whisper transcription
- [ ] Real-time streaming analysis
- [ ] Multi-language support (Korean, Mandarin)
- [ ] Confidence scores per action item

### 🚀 v2.0 — Future
- [ ] CRM integration (Salesforce, HubSpot)
- [ ] Slack/Teams bot deployment
- [ ] Custom keigo dictionary per company
- [ ] Dashboard with trend analysis across multiple meetings
- [ ] REST API endpoint for enterprise integration

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| AI Model | Ollama + qwen3:8b |
| Language Detection | langdetect |
| Export | Python json + fpdf2 |
| Deployment | Streamlit Community Cloud |

---

## 🤝 Contributing

Contributions are welcome! Especially:
- Additional Japanese business culture patterns
- New language support
- CRM integrations

```bash
git checkout -b feature/your-feature
git commit -m "Add your feature"
git push origin feature/your-feature
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

Built with ❤️ by [Kunal Bisht](https://github.com/Titankunal)

*"Boring projects. Infinite scale."*

⭐ **Star this repo if it helped you!** ⭐

</div>