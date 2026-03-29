"""
app.py
------
Main Streamlit application for the Call Transcript Analyzer.
Optimized for Japanese business culture analysis.

Run with:  streamlit run app.py
"""

import json
from datetime import datetime

import streamlit as st

from analyzer import analyze_transcript
from utils import (
    add_to_history,
    build_export_json,
    clean_text,
    detect_language,
    export_filename,
    format_history_label,
    language_display_name,
    parse_uploaded_file,
)

# ─────────────────────────────────────────────────────────────────────────────
# Page config (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TranscriptAI — Japanese Business Intelligence",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/your-repo/voice-analyzer",
        "Report a bug": "https://github.com/your-repo/voice-analyzer/issues",
        "About": "**TranscriptAI** — AI-powered call transcript analyzer with Japan-specific insights.",
    },
)

# ─────────────────────────────────────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+JP:wght@300;400;500;700&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Inter', 'Noto Sans JP', sans-serif;
}

/* ── App background ── */
.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    min-height: 100vh;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.04);
    border-right: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(12px);
}

[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #e2e8f0;
}

/* ── Cards ── */
.card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(8px);
    transition: border-color 0.2s ease;
}
.card:hover { border-color: rgba(139, 92, 246, 0.45); }

/* ── Metric cards ── */
.metric-card {
    background: linear-gradient(135deg, rgba(139,92,246,0.15), rgba(59,130,246,0.15));
    border: 1px solid rgba(139,92,246,0.30);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    text-align: center;
}
.metric-card .metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: #a78bfa;
}
.metric-card .metric-label {
    font-size: 0.78rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── Sentiment badges ── */
.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.04em;
}
.badge-positive { background: rgba(34,197,94,0.20); color: #4ade80; border: 1px solid rgba(74,222,128,0.35); }
.badge-neutral  { background: rgba(148,163,184,0.15); color: #94a3b8; border: 1px solid rgba(148,163,184,0.30); }
.badge-negative { background: rgba(239,68,68,0.20); color: #f87171; border: 1px solid rgba(248,113,113,0.35); }

/* ── Section headers ── */
.section-header {
    font-size: 1.05rem;
    font-weight: 600;
    color: #c4b5fd;
    letter-spacing: 0.04em;
    margin-bottom: 0.6rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid rgba(196,181,253,0.20);
}

/* ── Highlight box ── */
.highlight-box {
    background: linear-gradient(135deg, rgba(245,158,11,0.12), rgba(234,88,12,0.08));
    border-left: 3px solid #f59e0b;
    border-radius: 0 8px 8px 0;
    padding: 0.75rem 1rem;
    margin-bottom: 0.6rem;
    color: #fde68a;
    font-size: 0.9rem;
}

/* ── Action item card ── */
.action-item {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.6rem;
    border-left: 3px solid #8b5cf6;
}
.action-item .task-text { color: #e2e8f0; font-size: 0.95rem; font-weight: 500; }
.action-item .meta-text { color: #94a3b8; font-size: 0.8rem; margin-top: 0.3rem; }

/* ── Speaker bar ── */
.speaker-bar-wrap { margin-bottom: 1rem; }
.speaker-bar-label { color: #e2e8f0; font-size: 0.9rem; font-weight: 500; margin-bottom: 0.25rem; }
.speaker-bar-bg { background: rgba(255,255,255,0.08); border-radius: 999px; height: 10px; overflow: hidden; }
.speaker-bar-fill { height: 100%; border-radius: 999px;
    background: linear-gradient(90deg, #8b5cf6, #3b82f6); }

/* ── Tab styling ── */
[data-testid="stTabs"] button {
    color: #94a3b8 !important;
    font-weight: 500;
    border-radius: 8px 8px 0 0;
    padding: 0.5rem 1rem;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #a78bfa !important;
    border-bottom: 2px solid #8b5cf6 !important;
    background: rgba(139,92,246,0.10) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #4f46e5);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.55rem 1.5rem;
    font-weight: 600;
    font-size: 0.95rem;
    transition: all 0.2s ease;
    box-shadow: 0 4px 15px rgba(124,58,237,0.35);
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(124,58,237,0.5);
    background: linear-gradient(135deg, #6d28d9, #4338ca);
}

/* ── Upload area ── */
[data-testid="stFileUploader"] {
    border: 2px dashed rgba(139,92,246,0.35) !important;
    border-radius: 12px !important;
    background: rgba(139,92,246,0.05) !important;
}

/* ── Text area ── */
textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'Noto Sans JP', 'Inter', monospace !important;
}
textarea:focus {
    border-color: rgba(139,92,246,0.6) !important;
    box-shadow: 0 0 0 2px rgba(139,92,246,0.20) !important;
}

/* ── Progress bar ── */
.stProgress > div > div {
    background: linear-gradient(90deg, #7c3aed, #3b82f6) !important;
    border-radius: 999px !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] div[data-baseweb="select"] div {
    background: rgba(255,255,255,0.06) !important;
    border-color: rgba(255,255,255,0.12) !important;
    color: #e2e8f0 !important;
}

/* ── Info / warning boxes ── */
.stAlert { border-radius: 10px !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(139,92,246,0.4); border-radius: 3px; }

/* ── History item ── */
.history-item {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px;
    padding: 0.6rem 0.8rem;
    margin-bottom: 0.5rem;
    cursor: pointer;
    font-size: 0.82rem;
    color: #cbd5e1;
    transition: border-color 0.15s;
}
.history-item:hover { border-color: rgba(139,92,246,0.4); }
</style>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# Sample transcript
# ─────────────────────────────────────────────────────────────────────────────
SAMPLE_TRANSCRIPT = """田中: おはようございます、田中です。本日はお時間をいただきありがとうございます。
鈴木: こちらこそ、よろしくお願いいたします。鈴木です。
田中: まず、Q4の進捗についてご報告させていただきます。売上KPIは現時点で目標の98%に達しており、ほぼ計画通りです。
鈴木: そうですね、順調に進んでいるようで安心しました。ただ、新機能のリリーススケジュールについては、少し懸念がございます。
田中: Yes, I understand your concern. The release is scheduled for April 1st, but we may need a buffer.
鈴木: 検討いたします。技術チームとも相談してみますが、難しいかもしれません。できれば前向きに対応したいと思います。
田中: Understood. では、リリース日を田中さんの方でサインオフをいただければ、我々は準備を進めます。
鈴木: 承知しました。来週の月曜日までに確認いたします。
田中: ありがとうございます。次に、顧客からのフィードバック対応についてですが、サポートチームの増員が必要だと考えています。
鈴木: そうですね、確認してみます。サポートマニュアルの改訂も同時に進めた方が良いかもしれません。
田中: 同感です。鈴木さん、マニュアルのドラフト作成をお願いできますか？来週の金曜日までにレビュー用に提出していただければ。
鈴木: かしこまりました。対応いたします。
田中: では、次回のミーティングは来週金曜日の15:00に設定しましょう。議事録は田中が担当します。
鈴木: 承知いたしました。本日はありがとうございました。
田中: こちらこそ、よろしくお願いいたします。それでは失礼いたします。
鈴木: 失礼いたします。"""

# ─────────────────────────────────────────────────────────────────────────────
# Session state initialisation
# ─────────────────────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "results" not in st.session_state:
    st.session_state.results = None
if "current_transcript" not in st.session_state:
    st.session_state.current_transcript = ""
if "current_language" not in st.session_state:
    st.session_state.current_language = ""
if "transcript_text" not in st.session_state:
    st.session_state.transcript_text = ""


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style='text-align:center; padding: 1rem 0 0.5rem;'>
            <div style='font-size:2.5rem;'>🎙️</div>
            <div style='font-size:1.1rem; font-weight:700; color:#e2e8f0; margin-top:0.3rem;'>TranscriptAI</div>
            <div style='font-size:0.75rem; color:#94a3b8; margin-top:0.2rem;'>Japanese Business Intelligence</div>
        </div>
        <hr style='border-color:rgba(255,255,255,0.1); margin:1rem 0;'/>
        """,
        unsafe_allow_html=True,
    )

    # Language selector
    st.markdown(
        "<div class='section-header'>🌐 Language</div>", unsafe_allow_html=True
    )
    lang_choice = st.selectbox(
        "Select language",
        options=["Auto-detect", "Japanese (日本語)", "English"],
        label_visibility="collapsed",
        key="lang_select",
    )

    lang_map = {
        "Auto-detect": None,
        "Japanese (日本語)": "ja",
        "English": "en",
    }
    forced_lang = lang_map[lang_choice]

    st.markdown(
        "<hr style='border-color:rgba(255,255,255,0.08); margin:1rem 0;'/>",
        unsafe_allow_html=True,
    )

    # Analysis history
    st.markdown(
        "<div class='section-header'>🕘 Recent Analyses</div>", unsafe_allow_html=True
    )

    if not st.session_state.history:
        st.markdown(
            "<div style='color:#64748b; font-size:0.82rem; padding:0.5rem 0;'>No analyses yet.<br>Run your first analysis to see history here.</div>",
            unsafe_allow_html=True,
        )
    else:
        for i, entry in enumerate(st.session_state.history):
            label = format_history_label(entry)
            if st.button(
                f"📄 {label[:50]}…" if len(label) > 50 else f"📄 {label}",
                key=f"hist_{i}",
                use_container_width=True,
            ):
                st.session_state.results = entry["results"]
                st.session_state.current_transcript = entry["transcript"]
                st.session_state.current_language = entry["language"]
                st.session_state.transcript_text = entry["transcript"]
                st.rerun()

    st.markdown(
        "<hr style='border-color:rgba(255,255,255,0.08); margin:1rem 0;'/>",
        unsafe_allow_html=True,
    )

    # About
    with st.expander("ℹ️ About"):
        st.markdown(
            """
**TranscriptAI** analyzes meeting and call transcripts with specialized
support for Japanese business communication.

**Supported formats:** `.txt` `.vtt` `.json`

**Japan-specific features:**
- 敬語 (Keigo) register detection
- Nemawashi cue extraction
- Code-switching counter (JA↔EN)

*Swap the placeholder LLM in `analyzer.py` with Claude, GPT-4, or any API of your choice.*
""",
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Main header
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
<div style='text-align:center; padding: 2rem 0 1rem;'>
    <h1 style='font-size:2.4rem; font-weight:800; background:linear-gradient(135deg,#a78bfa,#60a5fa);
               -webkit-background-clip:text; -webkit-text-fill-color:transparent;
               background-clip:text; margin:0;'>
        🎙️ Call Transcript Analyzer
    </h1>
    <p style='color:#94a3b8; margin-top:0.5rem; font-size:1rem;'>
        AI-powered meeting intelligence · Japanese business culture optimized
    </p>
</div>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# Input section
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    "<div class='section-header'>📄 Transcript Input</div>", unsafe_allow_html=True
)

col_upload, col_paste = st.columns([1, 1], gap="large")

with col_upload:
    st.markdown(
        "<div style='color:#cbd5e1; font-size:0.85rem; margin-bottom:0.4rem;'>Upload a file</div>",
        unsafe_allow_html=True,
    )
    uploaded = st.file_uploader(
        "Upload transcript",
        type=["txt", "vtt", "json"],
        label_visibility="collapsed",
        key="file_uploader",
    )
    if uploaded is not None:
        parsed = parse_uploaded_file(uploaded)
        st.session_state.transcript_text = parsed
        st.success(f"✅ Loaded **{uploaded.name}** · {len(parsed):,} chars")

with col_paste:
    st.markdown(
        "<div style='color:#cbd5e1; font-size:0.85rem; margin-bottom:0.4rem;'>Or paste transcript</div>",
        unsafe_allow_html=True,
    )
    transcript_input = st.text_area(
        "Paste transcript",
        value=st.session_state.transcript_text,
        height=220,
        placeholder="Paste your transcript here…\n\nSupports Japanese, English, and mixed JA/EN text.",
        label_visibility="collapsed",
        key="paste_area",
    )
    if transcript_input != st.session_state.transcript_text:
        st.session_state.transcript_text = transcript_input

# Load sample button
col_btn_sample, col_btn_clear, col_spacer = st.columns([0.22, 0.18, 0.60])
with col_btn_sample:
    if st.button("📋 Load sample transcript", key="load_sample"):
        st.session_state.transcript_text = SAMPLE_TRANSCRIPT
        st.rerun()
with col_btn_clear:
    if st.button("🗑️ Clear", key="clear_input"):
        st.session_state.transcript_text = ""
        st.session_state.results = None
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# Analyse button
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

final_text = clean_text(st.session_state.transcript_text or "")
analyze_disabled = len(final_text.strip()) < 20

col_analyze, col_lang_display = st.columns([0.35, 0.65])

with col_analyze:
    run_analysis = st.button(
        "🔍 Analyze Transcript",
        key="run_analysis",
        disabled=analyze_disabled,
        use_container_width=True,
    )

with col_lang_display:
    if final_text:
        detected = detect_language(final_text)
        active_lang = forced_lang if forced_lang else detected
        st.markdown(
            f"<div style='padding-top:0.55rem; color:#94a3b8; font-size:0.87rem;'>"
            f"Detected: {language_display_name(detected)} &nbsp;|&nbsp; "
            f"Active: <span style='color:#a78bfa; font-weight:600;'>{language_display_name(active_lang)}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

if analyze_disabled and not final_text:
    st.info("Paste a transcript or upload a file to get started, then click **Analyze Transcript**.")

# ─────────────────────────────────────────────────────────────────────────────
# Run analysis
# ─────────────────────────────────────────────────────────────────────────────
if run_analysis and final_text:
    detected_lang = detect_language(final_text)
    active_lang = forced_lang if forced_lang else detected_lang

    progress_placeholder = st.empty()

    with progress_placeholder.container():
        progress_bar = st.progress(0, text="🔍 Detecting language…")
        progress_bar.progress(25, text="📊 Extracting features…")
        import time; time.sleep(0.4)
        progress_bar.progress(55, text="🤖 Running AI analysis…")

        with st.spinner("Analyzing transcript · this takes a few seconds…"):
            results = analyze_transcript(final_text, active_lang)

        progress_bar.progress(85, text="🎨 Formatting results…")
        time.sleep(0.3)
        progress_bar.progress(100, text="✅ Analysis complete!")
        time.sleep(0.4)

    progress_placeholder.empty()

    # Save results to session state
    st.session_state.results = results
    st.session_state.current_transcript = final_text
    st.session_state.current_language = active_lang

    # Add to history
    history_entry = {
        "timestamp": datetime.now().isoformat(),
        "language": active_lang,
        "snippet": final_text[:80],
        "transcript": final_text,
        "results": results,
    }
    st.session_state.history = add_to_history(
        st.session_state.history, history_entry
    )

    st.success("✅ Analysis complete! See results below.")
    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Results dashboard
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.results:
    results = st.session_state.results
    language = st.session_state.current_language
    transcript = st.session_state.current_transcript

    st.markdown(
        "<hr style='border-color:rgba(255,255,255,0.08); margin:1.5rem 0 1rem;'/>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='font-size:1.5rem; font-weight:700; color:#e2e8f0; margin-bottom:0.8rem;'>"
        "📊 Analysis Results"
        "</div>",
        unsafe_allow_html=True,
    )

    # Quick stats row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"<div class='metric-card'><div class='metric-value'>{len(results.get('speakers', []))}</div>"
            f"<div class='metric-label'>Speakers</div></div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"<div class='metric-card'><div class='metric-value'>{len(results.get('action_items', []))}</div>"
            f"<div class='metric-label'>Action Items</div></div>",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"<div class='metric-card'><div class='metric-value'>"
            f"{results.get('japan_insights', {}).get('code_switch_count', 0)}</div>"
            f"<div class='metric-label'>Code Switches</div></div>",
            unsafe_allow_html=True,
        )
    with c4:
        lang_name = language_display_name(language).split(" ", 1)[-1]
        st.markdown(
            f"<div class='metric-card'><div class='metric-value' style='font-size:1.3rem;'>{lang_name}</div>"
            f"<div class='metric-label'>Language</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # Export button
    export_json = build_export_json(transcript, language, results)
    st.download_button(
        label="⬇️ Export results as JSON",
        data=export_json.encode("utf-8"),
        file_name=export_filename(language),
        mime="application/json",
        key="export_btn",
    )

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────
    tab_summary, tab_actions, tab_sentiment, tab_speakers, tab_japan = st.tabs(
        ["📝 Summary", "✅ Action Items", "😊 Sentiment", "🎤 Speakers", "🇯🇵 Japan Insights"]
    )

    # ── Summary tab ───────────────────────────────────────────────────────
    with tab_summary:
        st.markdown("<div class='section-header'>Meeting Summary (TL;DR)</div>", unsafe_allow_html=True)
        for i, bullet in enumerate(results.get("summary", []), 1):
            st.markdown(
                f"<div class='card'>"
                f"<span style='color:#8b5cf6; font-weight:700; margin-right:0.5rem;'>{i}.</span>"
                f"<span style='color:#e2e8f0;'>{bullet}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # ── Action Items tab ──────────────────────────────────────────────────
    with tab_actions:
        st.markdown("<div class='section-header'>Action Items</div>", unsafe_allow_html=True)
        items = results.get("action_items", [])
        if not items:
            st.info("No action items were extracted from this transcript.")
        else:
            for item in items:
                task = item.get("task", "")
                owner = item.get("owner", "TBD")
                deadline = item.get("deadline", "TBD")
                st.markdown(
                    f"<div class='action-item'>"
                    f"<div class='task-text'>🔲 {task}</div>"
                    f"<div class='meta-text'>"
                    f"👤 <strong>Owner:</strong> {owner} &nbsp;·&nbsp; "
                    f"📅 <strong>Deadline:</strong> {deadline}"
                    f"</div></div>",
                    unsafe_allow_html=True,
                )

    # ── Sentiment tab ─────────────────────────────────────────────────────
    with tab_sentiment:
        st.markdown("<div class='section-header'>Speaker Sentiment</div>", unsafe_allow_html=True)

        sentiment_data = results.get("sentiment", [])
        if not sentiment_data:
            st.info("No sentiment data available.")
        else:
            for s in sentiment_data:
                speaker = s.get("speaker", "Unknown")
                label = s.get("label", "neutral").lower()
                score = s.get("score", "0.0")
                badge_cls = f"badge-{label}" if label in ("positive", "neutral", "negative") else "badge-neutral"
                icon = {"positive": "😊", "neutral": "😐", "negative": "😟"}.get(label, "😐")

                col_spk, col_badge, col_score = st.columns([0.45, 0.3, 0.25])
                with col_spk:
                    st.markdown(
                        f"<div class='card' style='padding:0.8rem 1rem; margin-bottom:0.4rem;'>"
                        f"<span style='color:#e2e8f0; font-weight:600;'>{icon} {speaker}</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                with col_badge:
                    st.markdown(
                        f"<div style='padding-top:0.55rem;'>"
                        f"<span class='badge {badge_cls}'>{label.upper()}</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                with col_score:
                    st.markdown(
                        f"<div style='padding-top:0.5rem; color:#94a3b8; font-size:0.88rem;'>"
                        f"Score: <strong style='color:#a78bfa;'>{score}</strong>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

    # ── Speakers tab ──────────────────────────────────────────────────────
    with tab_speakers:
        st.markdown("<div class='section-header'>Speaker Breakdown</div>", unsafe_allow_html=True)

        speakers_data = results.get("speakers", [])
        colors = ["#8b5cf6", "#3b82f6", "#10b981", "#f59e0b", "#ef4444"]

        if not speakers_data:
            st.info("No speaker data available.")
        else:
            for i, spk in enumerate(speakers_data):
                name = spk.get("name", f"Speaker {i+1}")
                pct = spk.get("talk_time_pct", 0)
                tone = spk.get("tone", "—")
                color = colors[i % len(colors)]

                col_info, col_bar = st.columns([0.4, 0.6])
                with col_info:
                    st.markdown(
                        f"<div class='card'>"
                        f"<div style='color:#e2e8f0; font-weight:600; font-size:1rem;'>🎤 {name}</div>"
                        f"<div style='color:#94a3b8; font-size:0.82rem; margin-top:0.3rem;'>Tone: {tone}</div>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                with col_bar:
                    st.markdown(
                        f"<div class='speaker-bar-wrap' style='padding-top:0.7rem;'>"
                        f"<div class='speaker-bar-label'>{pct}% talk time</div>"
                        f"<div class='speaker-bar-bg'>"
                        f"<div class='speaker-bar-fill' style='width:{pct}%; background:linear-gradient(90deg,{color},{color}aa);'></div>"
                        f"</div></div>",
                        unsafe_allow_html=True,
                    )

    # ── Japan Insights tab ────────────────────────────────────────────────
    with tab_japan:
        st.markdown("<div class='section-header'>🇯🇵 Japan Business Intelligence</div>", unsafe_allow_html=True)
        japan = results.get("japan_insights", {})

        # Keigo
        st.markdown(
            "<div style='color:#a78bfa; font-weight:600; font-size:0.9rem; margin:0.8rem 0 0.4rem;'>📜 Keigo Register (敬語レベル)</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='card'><span style='color:#fde68a;'>🏯 </span>"
            f"<span style='color:#e2e8f0;'>{japan.get('keigo_level', 'Not detected')}</span></div>",
            unsafe_allow_html=True,
        )

        # Nemawashi signals
        signals = japan.get("nemawashi_signals", [])
        st.markdown(
            f"<div style='color:#a78bfa; font-weight:600; font-size:0.9rem; margin:0.8rem 0 0.4rem;'>"
            f"🌱 Nemawashi Signals (根回し) — {len(signals)} detected</div>",
            unsafe_allow_html=True,
        )
        if signals:
            for sig in signals:
                st.markdown(
                    f"<div class='highlight-box'>🔸 {sig}</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                "<div class='card'><span style='color:#94a3b8;'>No nemawashi signals detected.</span></div>",
                unsafe_allow_html=True,
            )

        # Code-switch count
        cs = japan.get("code_switch_count", 0)
        st.markdown(
            f"<div style='color:#a78bfa; font-weight:600; font-size:0.9rem; margin:0.8rem 0 0.4rem;'>🔀 Code-Switching (JA↔EN)</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='card'>"
            f"<span style='font-size:1.8rem; font-weight:700; color:#60a5fa;'>{cs}</span>"
            f"<span style='color:#94a3b8; font-size:0.9rem; margin-left:0.6rem;'>language switches detected mid-conversation</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

        if cs == 0 and language == "ja":
            st.info("🇯🇵 Pure Japanese conversation — no English code-switching detected.")
        elif cs > 5:
            st.warning(
                f"⚡ High code-switching frequency ({cs} times) detected. "
                "This may indicate a globally-oriented team or international client interaction."
            )


# ─────────────────────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
<div style='text-align:center; padding:2rem 0 1rem; color:#475569; font-size:0.78rem;'>
    TranscriptAI · Powered by Streamlit · Japanese Business Intelligence Platform<br>
    <span style='color:#334155;'>Swap in your preferred LLM in <code>analyzer.py</code> · Supports Claude, GPT-4, Gemini</span>
</div>
""",
    unsafe_allow_html=True,
)
