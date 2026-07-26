# आनंदवाणी — AanandVaani MVP

**A voice AI spiritual companion — powered by Anand Ji Maharaj.**
Free beta until 20 July 2026.

---

## What This Is

A mobile-first web app that lets users have a live voice conversation with **Anand Ji Maharaj** — a fictional, original AI spiritual elder. Users speak in Hindi; Anand Ji listens, responds with wisdom from the Bhagavad Gita, Ramcharitmanas, and Upanishads, and replies in a warm, aged Hindi voice.

**Stack (100% free):**
| Layer | Technology | Cost |
|-------|-----------|------|
| Frontend | Static HTML + Web Speech API | Free (Vercel) |
| LLM | OpenRouter — `google/gemma-4-31b-it:free` | Free tier |
| TTS | Microsoft Edge TTS (`hi-IN-MadhurNeural`) | Free, no API key |
| Hosting | Vercel (frontend + backend) | Free tier |

---

## Project Structure

```
aanandvaani/
├── api/
│   └── index.py           ← FastAPI app (Vercerl serverless function)
├── public/
│   ├── index.html         ← Complete single-file app
│   ├── logo.png
│   ├── anandji.png
│   └── manifest.json
├── requirements.txt       ← Python dependencies (Vercerl reads from root)
├── vercel.json            ← Vercel routing config
├── .gitignore
└── README.md
```

---

## Deployment Guide (Vercel)

### Step 1 — Push to GitHub

```bash
cd anandji-mvp
git init
git add .
git commit -m "feat: AanandVaani MVP initial commit"
# Create a new repo on github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/aanandvaani.git
git push -u origin main
```

### Step 2 — Deploy to Vercel

1. Go to **vercel.com** → New Project → Import the GitHub repo
2. Vercel will auto-detect: Python backend + static frontend
3. Before deploying, add environment variable:
   - **OPENROUTER_API_KEY** = `sk-or-v1-...` (your OpenRouter API key)
4. Click **Deploy**
5. Vercel gives you a URL like `https://aanandvaani.vercel.app`

### Step 3 — Test

1. Open the Vercel URL on Chrome (desktop or Android)
2. Tap the mic button, speak in Hindi
3. Anand Ji replies with voice
4. Test `/health` endpoint: `https://your-url.vercel.app/health`

---

## Local Development

```bash
# Backend (serves frontend too)
cp backend/.env.example backend/.env
# Edit backend/.env with your OpenRouter key
pip install -r requirements.txt
cd backend && uvicorn main:app --reload --port 8000

# Frontend
# Open http://localhost:8000 in Chrome
```

---

## Key Configuration

| Variable | Default | Notes |
|----------|---------|-------|
| `OPENROUTER_API_KEY` | *(required)* | Get free at openrouter.ai |
| `OPENROUTER_MODEL` | `google/gemma-4-31b-it:free` | Free tier model |
| `TTS_VOICE` | `hi-IN-MadhurNeural` | Warm male Hindi voice |
| `TTS_RATE` | `-5%` | Slightly slower — natural elder pace |
| `TTS_PITCH` | `-8Hz` | Deeper — gravitas of a 75-year-old sant |

**Verified free models on OpenRouter (June 2026):**
- `google/gemma-4-31b-it:free` ← default, best Hindi
- `google/gemma-4-26b-a4b-it:free`
- `moonshotai/kimi-k2.6:free`

---

## Legal & Content Safety

- Anand Ji Maharaj is **entirely fictional** — no real person is imitated
- All wisdom sourced from **public domain** texts (Gita, Ramcharitmanas, Upanishads)
- Persona never gives medical, legal, or financial advice
- Persona never promotes any sect, temple, or organisation

---

*Built with ❤️ for Bharat. Free beta until 20 July 2026.*
