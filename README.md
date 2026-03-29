# 🎙️ TranscriptAI — Call Transcript Analyzer

> AI-powered meeting/call transcript analysis with specialized **Japanese business culture intelligence**.

## Features

| Feature | Details |
|---------|---------|
| **Input** | File upload (`.txt`, `.vtt`, `.json`) or paste |
| **Language** | Auto-detect Japanese · English · Mixed JA/EN |
| **AI Analysis** | Summary · Action items · Sentiment · Speakers |
| **Japan Intelligence** | Keigo register · Nemawashi signals · Code-switch counter |
| **Export** | Download full JSON report |
| **History** | Last 5 analyses stored in sidebar |

---

## Quick Start

### 1. Clone & Install

```bash
git clone <your-repo-url>
cd voice-analizer

pip install -r requirements.txt
```

### 2. Run locally

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

### 3. Try the sample

Click **"📋 Load sample transcript"** to load a built-in mixed JA/EN transcript and demo all features instantly.

---

## File Structure

```
voice-analizer/
├── app.py              # Main Streamlit app (UI, routing, session state)
├── analyzer.py         # analyze_transcript() — swap in real LLM here
├── utils.py            # Language detection, text parsing, export helpers
├── requirements.txt    # Python dependencies
├── .env.example        # API key template
└── README.md           # This file
```

---

## Swapping in a Real LLM

All AI logic lives in **`analyzer.py`**. The `analyze_transcript(text, language)` function currently returns a hardcoded mock response. To connect a real model:

### Anthropic Claude (recommended)

1. Install the SDK:
   ```bash
   pip install anthropic
   ```

2. Add your API key to Streamlit secrets (`/.streamlit/secrets.toml`):
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```

3. Edit `analyzer.py` — replace the mock return with:
   ```python
   import json, os
   from anthropic import Anthropic

   client = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

   def analyze_transcript(text: str, language: str) -> dict:
       prompt = build_prompt(text, language)
       message = client.messages.create(
           model="claude-opus-4-5",
           max_tokens=2048,
           messages=[{"role": "user", "content": prompt}]
       )
       return json.loads(message.content[0].text)
   ```

### OpenAI GPT-4

```python
from openai import OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": build_prompt(text, language)}],
    response_format={"type": "json_object"}
)
return json.loads(response.choices[0].message.content)
```

---

## JSON Schema (API contract)

The `analyze_transcript()` function always returns this schema:

```json
{
  "summary": ["bullet 1", "bullet 2", "bullet 3"],
  "action_items": [
    {"task": "string", "owner": "string", "deadline": "YYYY-MM-DD"}
  ],
  "sentiment": [
    {"speaker": "string", "score": "-1.0 to +1.0", "label": "positive|neutral|negative"}
  ],
  "speakers": [
    {"name": "string", "talk_time_pct": 0, "tone": "string"}
  ],
  "japan_insights": {
    "keigo_level": "description of politeness register",
    "nemawashi_signals": ["phrase — explanation"],
    "code_switch_count": 0
  }
}
```

---

## Deployment to Streamlit Community Cloud

1. Push your repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **"New app"** → select repo and branch → set **Main file: `app.py`**
4. Under **Advanced settings → Secrets**, paste:
   ```toml
   ANTHROPIC_API_KEY = "your-real-key"
   ```
5. Click **Deploy** — done!

> **Note:** The app runs with the mock analyzer by default (no API key needed).

---

## Environment Variables

Copy `.env.example` to `.env` for local development:

```bash
cp .env.example .env
```

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Claude API key (optional — only needed for real LLM) |
| `OPENAI_API_KEY` | OpenAI API key (if using GPT-4 instead) |

---

## Supported Transcript Formats

| Format | Notes |
|--------|-------|
| `.txt` | Plain text, speaker labels like `田中: …` |
| `.vtt` | WebVTT (Zoom, Teams, Google Meet) — timestamps stripped automatically |
| `.json` | Supports `{"transcript":"…"}`, `{"text":"…"}`, or utterance arrays `[{"speaker":"…","text":"…"}]` |

---

## Japan Business Culture Features

### Keigo (敬語) Register Detection
Classifies the politeness level used throughout the transcript:
- **丁寧語 (Teineigo)** — Standard polite (です/ます)
- **尊敬語 (Sonkeigo)** — Respectful (いらっしゃる, おっしゃる)
- **謙譲語 (Kenjōgo)** — Humble (いたします, 申し上げます)

### Nemawashi (根回し) Signal Extraction
Detects indirect communication patterns common in Japanese business:
- `検討いたします` — "We'll consider it" (often means polite refusal)
- `難しいかもしれません` — "That might be difficult" (implicit no)
- `前向きに対応します` — "We'll handle it positively" (vague commitment)

### Code-Switching Counter
Counts JA↔EN language switches to assess globalization level of the team/conversation.

---

*Built with [Streamlit](https://streamlit.io) · Designed for Japanese business teams*
