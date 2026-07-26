"""
AanandVaani Backend — v1.0.0-beta
Voice AI spiritual platform powered by Anand Ji Maharaj persona.

Stack:
  LLM  → OpenRouter (free tier models)
  TTS  → Microsoft Edge TTS via edge-tts (completely free, no key needed)
  STT  → Handled by browser Web Speech API (no backend needed)

Free beta until 20 July 2026.
"""

import base64
import logging
import os
import re
import time
import uuid
from typing import Optional

import edge_tts
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Load .env file if present (easier than shell export for local dev)
load_dotenv()

# ──────────────────────────────────────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# App & CORS
# ──────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="AanandVaani API",
    description="Backend for the Anand Ji Maharaj spiritual voice AI platform",
    version="1.0.0-beta",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Tighten in production
    allow_credentials=False,      # Must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────────────────────────────────────
# Configuration (set via environment variables)
# ──────────────────────────────────────────────────────────────────────────────

OPENROUTER_API_KEY: str  = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1/chat/completions"

# Free models on OpenRouter (verified June 2026):
#   google/gemma-4-31b-it:free     ← default, best Hindi quality
#   deepseek/deepseek-v4-flash:free
#   google/gemma-4-26b-a4b-it:free
#   moonshotai/kimi-k2.6:free
OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "google/gemma-4-31b-it:free")

# Fallback models tried in order if primary fails
FALLBACK_MODELS = [
    "deepseek/deepseek-v4-flash:free",
    "google/gemma-4-26b-a4b-it:free",
    "moonshotai/kimi-k2.6:free",
]

# Edge TTS voice for Anand Ji — warm Hindi male voice
TTS_VOICE: str  = os.getenv("TTS_VOICE",  "hi-IN-MadhurNeural")
TTS_RATE:  str  = os.getenv("TTS_RATE",   "-5%")    # Slightly slower than default — natural elder pace
TTS_PITCH: str  = os.getenv("TTS_PITCH",  "-8Hz")   # Deeper → gravitas of a 75-year-old sant

BETA_EXPIRY: str = "20 July 2026"

# ──────────────────────────────────────────────────────────────────────────────
# Anand Ji Maharaj — System Prompt
# ──────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are Anand Ji Maharaj (आनंद जी महाराज) — a fictional, original 75-year-old spiritual elder. You are a completely original fictional persona, NOT based on any real living or historical person.

PLATFORM: AanandVaani — a free spiritual voice companion for devotees across India.

WISDOM SOURCES (public domain only): Bhagavad Gita, Ramcharitmanas, Upanishads, and classical Hindi poetry (Kabir, Tulsidas, Mirabai, Surdas).

YOUR PERSONALITY:
• Warm, conversational Hindustani Hindi — like a loving grandfather
• Address users as "Beta" (son/daughter) or "Vatsa" (dear child)
• Listen first → comfort → then advise
• Short, warm responses: 2–4 sentences + ONE closing shloka/doha
• Never preachy, never judgmental, never repetitive

RESPONSE FORMAT (always follow this exactly):
1. Warm acknowledgment ("Haan Beta...", "Samajh sakta hoon...", "Aao Beta...")
2. Brief relevant spiritual wisdom
3. Gentle practical guidance rooted in dharma
4. ONE closing shloka, doha, or couplet — in original Sanskrit/Hindi/Braj — with brief meaning in parentheses

HARD RULES (never break):
• Never claim to be God or divine
• Never give medical, legal, or financial advice → redirect: "Woh toh doctor/vakeel se puchh lena Beta"
• Never name any specific temple, guru, organization, or political party
• Never mention any real living spiritual, religious, or political figure
• Never speak ill of any religion, caste, or community
• If asked your identity: "Main Anand Ji Maharaj hoon — ek aam insaan, jo thodi si zindagi jee chuka hai aur thoda samjha hai shaastron ko."

LANGUAGE: Respond in the SAME language the user uses. Hindi → respond in Hindi. English → respond in English. The closing shloka/doha is ALWAYS in its original language with a brief translation.

GREETING (on first message):
Hindi: "Jai Shree Ram, Beta. Main Anand Ji hoon. Bolo, aaj kya mann mein chal raha hai? Jo bhi ho, nishchintr hokar kaho — main yahan hoon. ॐ"
English: "Jai Shree Ram, dear child. I am Anand Ji. Tell me, what weighs on your heart today? Speak freely — I am listening. ॐ"

EXAMPLE RESPONSE (Hindi):
"Haan Beta, teri baat sunke dil bhar aaya mera. Zindagi mein andhera kabhi kabhi bahut gehara lagta hai — par yaad rakh, raat kitni bhi lambi ho, sawera zaroor aata hai. Bas is pal mein reh, Ishwar pe bharosa rakh.

'करते करते अभ्यास के, जड़मति होत सुजान।
रसरी आवत जात तें, सिल पर परत निशान।।'
(Kabir: With practice even a slow mind becomes wise — just as rope passing over stone leaves its mark.)"

EXAMPLE RESPONSE (English):
"Yes my child, I feel the weight in your words. Life sometimes places us in darkness so deep it seems endless — but no night lasts forever, dawn always comes. Rest in this moment and trust the divine.

'नहिं कोउ अस जनमा जग माहीं। प्रभुता पाइ जाहि मद नाहीं।।'
(Ramcharitmanas: No one born in this world gains power without some pride rising — stay humble, Beta.)"
"""

# Greeting text for the /api/greeting endpoint
GREETING_HI = "जय श्री राम, बेटा। मैं आनंद जी हूँ। बताओ, आज क्या मन में चल रहा है? जो भी हो, निःसंकोच कहो मुझसे। मैं यहाँ हूँ। ॐ शान्तिः।"
GREETING_EN = "Jai Shree Ram, dear child. I am Anand Ji Maharaj. Tell me, what weighs on your heart today? Speak freely — I am listening. Om Shanti."

# ──────────────────────────────────────────────────────────────────────────────
# Session Management (in-memory, sufficient for MVP ~200 users)
# ──────────────────────────────────────────────────────────────────────────────

sessions: dict[str, dict] = {}
SESSION_MAX_MESSAGES = 24   # 12 conversation turns
SESSION_TTL_SECONDS   = 86400  # 24 hours


def get_or_create_session(session_id: Optional[str]) -> tuple[str, dict]:
    now = time.time()

    # Lazy cleanup of expired sessions
    expired_keys = [k for k, v in sessions.items() if now - v["last_access"] > SESSION_TTL_SECONDS]
    for k in expired_keys:
        del sessions[k]

    if not session_id or session_id not in sessions:
        session_id = str(uuid.uuid4())
        sessions[session_id] = {"history": [], "last_access": now}
        logger.info(f"New session: {session_id}")
    else:
        sessions[session_id]["last_access"] = now

    return session_id, sessions[session_id]


# ──────────────────────────────────────────────────────────────────────────────
# LLM — OpenRouter
# ──────────────────────────────────────────────────────────────────────────────

async def _call_openrouter(model: str, messages: list, headers: dict) -> str:
    """Single OpenRouter call — raises on any failure."""
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 400,
        "temperature": 0.75,
    }
    async with httpx.AsyncClient(timeout=35.0) as client:
        resp = await client.post(OPENROUTER_BASE_URL, headers=headers, json=payload)

    if resp.status_code != 200:
        body = resp.text[:300]
        logger.error(f"OpenRouter [{model}] {resp.status_code}: {body}")
        raise RuntimeError(f"HTTP {resp.status_code}: {body}")

    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()


async def call_llm(user_text: str, history: list[dict]) -> str:
    if not OPENROUTER_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="OPENROUTER_API_KEY not set. Create backend/.env with OPENROUTER_API_KEY=sk-or-...",
        )

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history[-SESSION_MAX_MESSAGES:])
    messages.append({"role": "user", "content": user_text})

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://aanandvaani.vercel.app",
        "X-Title": "AanandVaani",
    }

    # Try primary model first, then fallbacks
    models_to_try = [OPENROUTER_MODEL] + FALLBACK_MODELS
    last_error = None

    for model in models_to_try:
        try:
            logger.info(f"Trying model: {model}")
            return await _call_openrouter(model, messages, headers)
        except httpx.TimeoutException:
            last_error = f"Timeout on {model}"
            logger.warning(last_error)
        except RuntimeError as e:
            last_error = str(e)
            logger.warning(f"Model {model} failed: {last_error} — trying next")
            continue

    raise HTTPException(status_code=502, detail=f"All models failed. Last error: {last_error}")


# ──────────────────────────────────────────────────────────────────────────────
# TTS — Microsoft Edge TTS (free, no API key)
# ──────────────────────────────────────────────────────────────────────────────

def _strip_markdown(text: str) -> str:
    """Clean markdown so TTS doesn't read asterisks, hashes, etc."""
    text = re.sub(r"\*{1,3}(.+?)\*{1,3}", r"\1", text)   # bold/italic
    text = re.sub(r"#{1,6}\s+", "", text)                   # headings
    text = re.sub(r"`{1,3}(.+?)`{1,3}", r"\1", text)       # code
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)         # links
    return text.strip()


async def synthesize_speech(text: str) -> bytes:
    """Return raw MP3 bytes using Edge TTS — completely free."""
    clean = _strip_markdown(text)

    communicate = edge_tts.Communicate(
        clean,
        TTS_VOICE,
        rate=TTS_RATE,
        pitch=TTS_PITCH,
    )

    chunks: list[bytes] = []
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            chunks.append(chunk["data"])

    if not chunks:
        raise RuntimeError("Edge TTS returned no audio data")

    return b"".join(chunks)


# ──────────────────────────────────────────────────────────────────────────────
# API Endpoints
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "model": OPENROUTER_MODEL,
        "tts_voice": TTS_VOICE,
        "beta_free_until": BETA_EXPIRY,
        "active_sessions": len(sessions),
        "api_key_set": bool(OPENROUTER_API_KEY),
    }


@app.get("/api/debug")
async def debug():
    """Tests all models in fallback order — shows which one works right now."""
    if not OPENROUTER_API_KEY:
        return {"ok": False, "error": "OPENROUTER_API_KEY not set in .env or environment"}

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    test_msg = [{"role": "user", "content": "Say 'Jai Shree Ram' in one line only."}]
    results = []

    for model in [OPENROUTER_MODEL] + FALLBACK_MODELS:
        try:
            response = await _call_openrouter(model, test_msg, headers)
            return {"ok": True, "working_model": model, "response": response, "tried": results}
        except Exception as e:
            results.append({"model": model, "error": str(e)[:120]})

    return {"ok": False, "error": "All models failed", "details": results}


@app.get("/api/greeting")
async def get_greeting(lang: str = "hi"):
    """
    Returns Anand Ji's opening greeting as text + base64 MP3 audio.
    Called once when the frontend loads to give users an immediate warm welcome.
    """
    text = GREETING_HI if lang == "hi" else GREETING_EN

    audio_b64: Optional[str] = None
    try:
        audio_bytes = await synthesize_speech(text)
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    except Exception as exc:
        logger.warning(f"Greeting TTS failed: {exc}")
        # Return without audio — frontend will still show the text

    return {
        "text": text,
        "audio": audio_b64,
        "session_id": str(uuid.uuid4()),
    }


class ChatRequest(BaseModel):
    text: str
    session_id: Optional[str] = None


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Main conversation endpoint.
    Input : transcribed text from the browser + optional session_id
    Output: Anand Ji's text response + base64 MP3 audio + session_id
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Empty message")

    session_id, session = get_or_create_session(request.session_id)

    # ── Call LLM ────────────────────────────────────────────────────────────
    try:
        response_text = await call_llm(request.text, session["history"])
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"LLM unexpected error: {exc}")
        response_text = (
            "Beta, abhi thodi takneeki samasya aa gayi hai. "
            "Thodi der baad phir try karo — Ishwar sada hamare saath hain. ॐ"
        )

    # Update conversation history
    session["history"].append({"role": "user",      "content": request.text})
    session["history"].append({"role": "assistant", "content": response_text})

    # Trim history to keep memory bounded
    if len(session["history"]) > SESSION_MAX_MESSAGES:
        session["history"] = session["history"][-SESSION_MAX_MESSAGES:]

    # ── Call TTS ─────────────────────────────────────────────────────────────
    audio_b64: Optional[str] = None
    try:
        audio_bytes = await synthesize_speech(response_text)
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    except Exception as exc:
        logger.warning(f"TTS error (response will be text-only): {exc}")

    return {
        "response":   response_text,
        "audio":      audio_b64,          # None if TTS failed — frontend handles gracefully
        "session_id": session_id,
    }


class ResetRequest(BaseModel):
    session_id: Optional[str] = None


@app.post("/api/reset")
async def reset_session(body: ResetRequest):
    """Clear the conversation history for a session (start fresh)."""
    sid = body.session_id
    if sid and sid in sessions:
        del sessions[sid]
        logger.info(f"Session reset: {sid}")
    new_sid = str(uuid.uuid4())
    return {"message": "Session reset. Anand Ji is ready.", "session_id": new_sid}
