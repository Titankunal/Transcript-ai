# sample_transcripts.py
# Test transcripts for TranscriptAI
#
# Purpose:
#   1. Verify trilingual detection (Hindi + English + Japanese)
#   2. Verify cross-script name resolution:
#      - Tanaka (Romaji) == 田中 (Kanji) == same speaker
#      - Priya (English) == प्रिया (Devanagari) == same speaker
#   3. Stress-test all NLP layers simultaneously
#   4. Pre-cache in vector store for instant demo loading

# ── SAMPLE 1: TRILINGUAL BUSINESS MEETING ────────────────────────────────────
# Tests:
#   - Priya referred as both "Priya" and "प्रिया" in same transcript
#   - Tanaka referred as both "Tanaka" and "田中" in same transcript
#   - Hindi soft rejections: dekhte hain, thoda mushkil
#   - Japanese soft rejections: 検討いたします, 難しいかもしれません
#   - English hedging: circle back, let me see what I can do
#   - Code switching: EN→HI→JA within single conversation

SAMPLE_TRILINGUAL = """Rahul: Good morning everyone. Aaj hum Q3 product launch ke baare mein discuss karenge.
Priya: Haan, main ready hoon. Mujhe kuch concerns hain about the timeline.
田中: おはようございます。よろしくお願いいたします。
Rahul: Tanaka-san, can you give us the Japan market update first?
田中: はい。Q3の日本市場では、売上目標の92%に達しています。ただ、新機能のリリースについては少し懸念がございます。
Priya: Tanaka, yeh concern kya hai exactly? Timeline issue hai ya technical?
田中: 検討いたします。Technical team se confirm karna padega. It might be difficult to meet the October deadline.
Rahul: Okay. प्रिया, kya tum India market ka update de sakti ho?
Priya: Haan bilkul. India mein hum 87% pe hain. Main blocker hai ki support team short-staffed hai.
Rahul: Yeh serious issue hai. Priya, can you prepare a staffing proposal by Friday?
Priya: Dekhte hain. Thoda mushkil hai but koshish karenge. I'll try to have something by end of week.
Rahul: That's not a commitment. I need a yes or no — Friday tak hoga ya nahi?
Priya: Okay, yes. Friday tak de dungi.
田中: 承知しました。Japan side se bhi ek resource provide kar sakte hain if needed.
Rahul: Perfect. Toh summary karte hain — 田中 will confirm technical timeline by Wednesday.
田中: はい、水曜日までに確認いたします。
Rahul: And Priya is committed to staffing proposal by Friday. Next meeting Monday 10am.
Priya: Confirmed. See you Monday.
田中: お疲れ様でした。よろしくお願いします。"""


# ── SAMPLE 2: HIGH-CONFLICT MEETING ──────────────────────────────────────────
# Tests:
#   - Aggressive tone detection (Client)
#   - Deferential tone detection (Kenji)
#   - Escalation signals in English
#   - Japanese soft rejection under pressure
#   - PII: phone number, email in transcript
#   - Name: Kenji (Romaji) — no Kanji equivalent to test Romaji-only path

SAMPLE_HIGH_CONFLICT = """Client: This is completely unacceptable. The system has been down for 6 hours.
Kenji: 大変申し訳ございません。We are working on it as fast as possible.
Client: You said the same thing yesterday. This is the second major outage this month.
Kenji: はい、ご指摘の通りです。The server team is investigating. 難しい状況ですが、今週中に解決します。
Client: I don't want "we're investigating." I need a written commitment. My boss wants answers by 3pm.
Kenji: ご要望はよく分かりました。上司に相談して、2時間以内に書面でご回答します。
Client: Fine. And I want your direct line — not the helpdesk. Call me at +91-9876543210.
Kenji: 承知しました。My email is kenji.yamada@techcorp.jp — I will contact you directly.
Client: If this isn't resolved by Friday we will reconsider the entire contract.
Kenji: 誠に申し訳ございません。全力で対応いたします。We will not let that happen.
Client: I hope not. This is the last warning.
Kenji: はい。I will personally ensure resolution. お電話もお待ちしております。"""


# ── SAMPLE 3: INTERNAL HINGLISH STANDUP ──────────────────────────────────────
# Tests:
#   - Pure Hinglish (no Japanese)
#   - Hindi NLP layer exclusively
#   - Hierarchical yes: jo aap kahenge, haan haan bilkul
#   - Jugaad framing: kuch na kuch ho jayega, manage ho jayega
#   - Face-saving exit: upar se baat karta hoon
#   - Speaker: Vikram referred as both "Vikram" and "Vikram bhai" — normalization test
#   - Devanagari mixed in: देखते हैं, ठीक है

SAMPLE_HINGLISH_STANDUP = """Sharma Sir: Toh batao, sprint ka kya status hai? Deadline kal hai.
Vikram: Haan sir, almost done hai. Bas ek bug hai jo thoda mushkil hai.
Sharma Sir: Thoda mushkil matlab? Done hoga ya nahi kal tak?
Vikram: Haan haan bilkul sir. Koshish karenge. देखते हैं, manage ho jayega.
Sharma Sir: Vikram bhai, yeh "dekhte hain" waali baat band karo. Straight bolo.
Vikram: Sir sach mein thodi problem hai. Backend mein ek race condition hai jo intermittently aati hai.
Priya: Main help kar sakti hoon Vikram ko. Mujhe yeh issue pata hai.
Sharma Sir: Priya, kya tum kal tak fix kar sakti ho?
Priya: Haan sir, main kar sakti hoon. 100% committed hoon.
Vikram: Main bhi karta hoon sir. Upar se baat karta hoon agar koi blocker aaya.
Sharma Sir: Upar matlab? Seedha mujhe batao, upar-neeche mat karo.
Vikram: Ji sir. Aap jo theek samjhe. Main directly aapko update dunga.
Sharma Sir: ठीक है। Priya lead karegi is fix pe. Vikram support karega. Deal?
Priya: Deal sir. Kal subah 10 baje update dunga — I mean dungi.
Vikram: Aur agar nahi hua toh kuch na kuch ho jayega sir, don't worry.
Sharma Sir: Yahi sab mat bolna. Bas karo. Meeting khatam."""


# ── LANGUAGE METADATA ─────────────────────────────────────────────────────────
SAMPLE_METADATA = {
    "SAMPLE_TRILINGUAL": {
        "language":    "mixed",
        "description": "Trilingual — Hindi + English + Japanese with cross-script name switching",
        "name_tests": [
            ("Priya", "प्रिया", "same speaker"),
            ("Tanaka", "田中",   "same speaker"),
        ],
        "expected_signals": {
            "hindi":    ["dekhte hain", "thoda mushkil", "koshish karenge"],
            "japanese": ["検討いたします", "難しいかもしれません", "少し懸念"],
            "english":  [],
        }
    },
    "SAMPLE_HIGH_CONFLICT": {
        "language":    "mixed",
        "description": "High-conflict EN+JA — escalation, PII masking, aggressive tone",
        "name_tests": [
            ("Kenji", "Kenji", "Romaji only — no kanji variant"),
        ],
        "expected_signals": {
            "japanese": ["ご要望はよく分かりました", "上司に相談", "難しい状況"],
            "english":  ["reconsider", "unacceptable", "last warning"],
        }
    },
    "SAMPLE_HINGLISH_STANDUP": {
        "language":    "hi",
        "description": "Pure Hinglish standup — Hindi NLP layer only, no Japanese",
        "name_tests": [
            ("Vikram", "Vikram bhai", "honorific normalization test"),
        ],
        "expected_signals": {
            "hindi": ["thoda mushkil", "dekhte hain", "koshish karenge",
                      "haan haan bilkul", "upar se baat karta hoon",
                      "aap jo theek samjhe", "kuch na kuch ho jayega"],
        }
    },
}


if __name__ == "__main__":
    """
    Pre-cache all sample transcripts in vector store.
    Run once: python tests/sample_transcripts.py
    """
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    samples = [
        (SAMPLE_TRILINGUAL,       "mixed", "Trilingual meeting"),
        (SAMPLE_HIGH_CONFLICT,    "mixed", "High-conflict EN+JA"),
        (SAMPLE_HINGLISH_STANDUP, "hi",    "Hinglish standup"),
    ]

    print("Pre-caching sample transcripts into vector store...")
    print()

    for transcript, language, name in samples:
        print(f"  [{name}]")

        # Check if already cached
        try:
            from utils.vector_cache import get_cached_result, store_result, is_available
            if is_available():
                cached = get_cached_result(transcript, language)
                if cached:
                    sim = cached.get("_cache_similarity", 0)
                    print(f"    ✅ Already in vector cache ({sim:.0%} similarity)")
                    continue
        except ImportError:
            print("    ⚠ vector_cache not available")
            continue

        # Analyze and store
        from analysis.analyzer import analyze_transcript
        print(f"    → Analyzing ({language})...")
        result = analyze_transcript(transcript, language)
        provider = result.get("_provider","?")
        duration = result.get("_duration_ms",0)

        if "mock" not in provider:
            store_result(transcript, language, result)
            print(f"    ✅ Stored | {provider} | {duration/1000:.1f}s")
            print(f"    Summary: {result.get('summary',[''])[0][:70]}...")
        else:
            print(f"    ❌ Mock result — check GROQ_API_KEY")
        print()

    print("Done. All samples ready in vector store.")