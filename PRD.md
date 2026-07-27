# आनंदवाणी (AanandVaani) — Product Requirements Document

**Version:** 1.0.0-beta
**Last Updated:** 27 July 2026
**Status:** Live on Vercel — Free beta until 20 July 2026

---

## 1. Product Vision

A mobile-first voice AI spiritual companion that lets users have a real-time voice conversation with **Anand Ji Maharaj** — a warm, fictional 75-year-old spiritual elder. Users speak in Hindi; Anand Ji listens, responds with wisdom from public domain scriptures, and replies in a natural aged Hindi voice.

**Mission:** Make spiritual guidance accessible to every Indian — free, private, no app download needed.

---

## 2. Current Tech Stack

| Layer | Technology | Cost | Status |
|-------|-----------|------|--------|
| Frontend | Single-file HTML/CSS/JS (PWA) | Free (Vercel) | ✅ Live |
| STT | Web Speech API (browser-native) | Free | ✅ Live |
| LLM | OpenRouter — `deepseek/deepseek-v4-flash:free` | Free tier | ✅ Live |
| TTS | Microsoft Edge TTS (`hi-IN-MadhurNeural`) | Free, no key | ✅ Live |
| Backend | FastAPI (Python) | Free (Vercel serverless) | ✅ Live |
| Hosting | Vercel | Free tier | ✅ Live |

---

## 3. Current Features (v1.0.0-beta)

### 3.1 Voice Conversation
- Tap mic → speak Hindi → Anand Ji responds with voice + text
- Web Speech API for browser-native STT (no backend needed)
- Edge TTS for natural Hindi male voice (MadhurNeural)
- Rate: +8%, Pitch: -8Hz — elder gravitas

### 3.2 Anand Ji Persona
- Warm grandfather tone — listens first, comforts, then advises
- Responses: 2–4 sentences + ONE closing shloka/doha
- Mixed-Script Protocol: Hindi in Devanagari, technical words in English
- Wisdom from: Bhagavad Gita, Ramcharitmanas, Upanishads, Kabir, Tulsidas

### 3.3 UI/UX
- Saffron sunrise temple theme
- Animated avatar ring (idle/recording/processing/speaking states)
- Turnwise scrolling (each Q&A pair scrolls together)
- WhatsApp share button on responses
- Help overlay with usage instructions
- PWA manifest (add to homescreen on Android)

### 3.4 Backend
- Session management (in-memory, 24h TTL, 12-turn memory)
- Model fallback chain: deepseek → gemma-31b → gemma-26b → kimi
- Health check endpoint (`/health`)
- Debug endpoint (`/api/debug`) — tests all models
- Greeting endpoint (`/api/greeting`) — TTS pre-generated welcome

### 3.5 Safety
- Anand Ji is entirely fictional — no real person imitated
- Never gives medical/legal/financial advice
- Never names temples, gurus, or political figures
- Never speaks ill of any religion/caste/community
- All scriptures sourced from public domain texts

---

## 4. Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Frontend (PWA)                    │
│            Single HTML file — index.html             │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │ Web      │  │ Fetch    │  │ Audio Player     │   │
│  │ Speech   │→ │ POST /   │→ │ (base64 MP3)     │   │
│  │ API (STT)│  │ api/chat │  │                  │   │
│  └──────────┘  └──────────┘  └──────────────────┘   │
└──────────────────────┬──────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────┐
│              Backend (FastAPI Serverless)             │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │ OpenRouter│  │ Edge TTS │  │ Session Store    │   │
│  │ (LLM)    │  │ (MP3)    │  │ (in-memory)      │   │
│  └──────────┘  └──────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────┘
```

---

## 5. API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Serves frontend HTML |
| GET | `/health` | Health check + model status |
| GET | `/api/debug` | Tests all fallback models |
| GET | `/api/greeting?lang=hi` | Returns greeting text + audio |
| POST | `/api/chat` | Main conversation endpoint |
| POST | `/api/reset` | Clear session history |

---

## 6. Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | *(required)* | OpenRouter API key |
| `OPENROUTER_MODEL` | `deepseek/deepseek-v4-flash:free` | Primary LLM |
| `TTS_VOICE` | `hi-IN-MadhurNeural` | Edge TTS voice |
| `TTS_RATE` | `+8%` | Speaking speed |
| `TTS_PITCH` | `-8Hz` | Voice pitch |

---

## 7. Project Structure

```
anandji-mvp/
├── api/
│   ├── handler.py              ← Vercel serverless entry (primary)
│   └── index.py                ← Vercel catch-all fallback
├── backend/
│   ├── main.py                 ← Local dev server (uvicorn)
│   ├── .env                    ← API keys (git-ignored)
│   ├── .env.example            ← Template
│   └── requirements.txt        ← Python dependencies
├── frontend/
│   ├── index.html              ← Single-file PWA (HTML/CSS/JS)
│   ├── logo.png                ← App icon
│   ├── anandji.png             ← Avatar image
│   └── manifest.json           ← PWA manifest
├── public/                     ← Legacy (pre-refactor)
├── vercel.json                 ← Vercel routing config
├── requirements.txt            ← Root requirements (Vercel reads this)
├── README.md
└── PRD.md                      ← This document
```

---

## 8. Next Features — Roadmap

### 🔴 Phase 1: Stability & Polish (Week 1–2)

| # | Feature | Priority | Effort | Description |
|---|---------|----------|--------|-------------|
| 1.1 | **Error boundary & retry UX** | P0 | 2h | Auto-retry on TTS/LLM failure with exponential backoff. Show retry button with countdown. |
| 1.2 | **Streaming TTS** | P0 | 6h | Stream audio chunks as they're generated instead of waiting for full MP3. Reduces perceived latency by 2–3s. |
| 1.3 | **Input validation & sanitization** | P0 | 2h | Sanitize user input, limit message length (200 chars), rate-limit per session. |
| 1.4 | **Offline fallback message** | P1 | 1h | Show cached greeting + "connect to internet" when offline. |
| 1.5 | **Mobile Safari STT fix** | P1 | 3h | Safari Web Speech API gives no `isFinal` — detect and use interim transcript fallback. |
| 1.6 | **README update** | P1 | 1h | Update README to reflect current model (deepseek), new greeting, and correct project structure. |

### 🟡 Phase 2: UX & Engagement (Week 3–4)

| # | Feature | Priority | Effort | Description |
|---|---------|----------|--------|-------------|
| 2.1 | **Conversation history (localStorage)** | P1 | 4h | Persist last 10 messages in localStorage so conversation survives page refresh. |
| 2.2 | **Text input mode** | P1 | 4h | Add a text input field for users who can't use mic (noisy env, speech issues). |
| 2.3 | **Dark mode** | P2 | 3h | Temple night theme — dark mahogany background, warm gold accents. Toggle in header. |
| 2.4 | **Response bookmarking** | P2 | 3h | Star/bookmark favorite responses. Saved in localStorage. View saved shlokas. |
| 2.5 | **Daily shloka notification** | P2 | 5h | PWA push notification with a random shloka + meaning every morning. |
| 2.6 | **Share as image** | P2 | 4h | Generate a branded shloka card (canvas → PNG) for Instagram/WhatsApp stories. |

### 🟢 Phase 3: Intelligence & Personalization (Week 5–8)

| # | Feature | Priority | Effort | Description |
|---|---------|----------|--------|-------------|
| 3.1 | **Topic memory** | P1 | 6h | Remember user's main concern across sessions (stored in localStorage). Anand Ji references it: "पिछली बार तुमने बताया था..." |
| 3.2 | **Language detection & auto-switch** | P1 | 3h | Auto-detect Hindi vs English vs Hinglish. Adjust response language. |
| 3.3 | **Mood-based response tuning** | P2 | 4h | Detect user mood from speech/text (happy/sad/anxious). Adjust tone and shloka selection. |
| 3.4 | **Multi-language support** | P2 | 8h | Add Marathi, Gujarati, Tamil, Bengali, Telugu voices + language-specific personas. |
| 3.5 | **Scripture knowledge base** | P2 | 10h | Structured index of shlokas by topic (anxiety, grief, devotion, karma). LLM picks from curated list instead of generating. |

### 🔵 Phase 4: Scale & Monetization (Month 3+)

| # | Feature | Priority | Effort | Description |
|---|---------|----------|--------|-------------|
| 4.1 | **User accounts (Firebase Auth)** | P1 | 8h | Google/phone login. Sync history across devices. |
| 4.2 | **Analytics dashboard** | P1 | 5h | Track: sessions, avg conversation length, top topics, drop-off points. |
| 4.3 | **Premium tier** | P2 | 12h | Faster models (GPT-4o, Claude), longer conversations, priority TTS, ad-free. |
| 4.4 | **API for developers** | P3 | 10h | Let devs build spiritual apps on top of AanandVaani API. |
| 4.5 | **Voice cloning (Anand Ji)** | P3 | 8h | Train a custom voice with ElevenLabs for consistent, branded speech. |

---

## 9. Technical Debt & Known Issues

| Issue | Severity | Description |
|-------|----------|-------------|
| In-memory sessions | 🔴 High | Sessions lost on cold start. Vercel serverless reboots = all history gone. Need Redis/Upstash. |
| Hardcoded INDEX_HTML in `api/index.py` | 🟡 Medium | Was hardcoded, now reads from file. But `vercel.json` routes `/api/(.*)` → `index.py`, not `handler.py`. |
| `public/` vs `frontend/` duplication | 🟡 Medium | Two copies of index.html. `public/` is legacy, `frontend/` is canonical. Clean up `public/`. |
| No rate limiting | 🟡 Medium | Anyone can spam the API. Add per-IP rate limiting. |
| No HTTPS redirect | 🟢 Low | Vercel handles this, but explicit config is safer. |

---

## 10. Success Metrics

| Metric | Target (Beta) | Target (v1.0) |
|--------|---------------|---------------|
| Daily Active Users | 50 | 500 |
| Avg. session duration | 3 min | 5 min |
| Avg. turns per session | 4 | 6 |
| TTS success rate | >90% | >98% |
| LLM response time | <8s | <4s |
| PWA install rate | — | >15% |

---

## 11. Competitive Landscape

| Competitor | Differentiation |
|-----------|----------------|
| ChatGPT / Gemini | Generic, not spiritual, not Hindi-first |
| Pray.com / Abide | English-only, Christian-focused |
| Hindu spiritual apps | Text-based, no voice conversation |
| **AanandVaani** | Hindi voice-first, spiritual persona, free, no app download |

**Our moat:** Voice-native spiritual companion in Hindi — zero friction (PWA, no install), culturally authentic persona, 100% free during beta.

---

*Built with ❤️ for Bharat. Free beta until 20 July 2026.*
