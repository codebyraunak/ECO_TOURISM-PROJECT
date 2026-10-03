from __future__ import annotations

import logging
import os
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are EcoGuide, the official AI travel assistant for EcoKarnataka — a responsible nature and eco-tourism platform for Karnataka, India.

Your mission is to help travelers explore Karnataka's breathtaking natural landscapes, heritage, wildlife, and culture responsibly with minimal ecological footprint.

You assist travelers with:
- Natural & eco-tourism destinations (Western Ghats, waterfalls, beaches, hill stations, rainforests, valleys)
- Wildlife sanctuaries & national parks (Bandipur, Nagarhole, Kudremukh, Dandeli, Bhadra, BR Hills, Anshi)
- Heritage & cultural landmarks (Hampi, Badami, Pattadakal, Belur, Halebidu, Bijapur, Mysore)
- Trekking trails, permits, best seasons, and safety (Kumara Parvatha, Tadiandamol, Kudremukh, Mullayanagiri)
- Sustainable eco-homestays, community tourism, and authentic local experiences
- Local cuisine (Neer Dosa, Jolada Rotti, Ragi Mudde, Mangalorean specialties, Coorg delicacies)
- Ethical travel practices (Leave No Trace, plastic-free travel, wildlife etiquette, respecting local culture)
- Custom day-by-day itineraries and budget-conscious sustainable planning
- Transportation options (KSRTC eco-routes, train connectivity, shared green transit)

Tone and style:
- Friendly, inspiring, practical, concise, and structured.
- Use clear bullet points and short paragraphs for easy reading on mobile and web.
- Emphasize safety, sustainability, and respecting local biodiversity.
"""


def get_genai_client():
    """Lazily initialize and return the Google GenAI client if configured."""
    api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except Exception as exc:
        logger.warning("Failed to initialize Google GenAI client: %s", exc)
        return None


def generate_response(message: str, language: str = "English") -> str:
    """Generate an AI guide response for travel queries about Karnataka."""
    client = get_genai_client()

    if not client:
        # Informative fallback when API key is not yet set in environment
        return (
            "🌿 **Welcome to EcoGuide Karnataka!**\n\n"
            "I am your AI travel companion for discovering Karnataka's pristine forests, wildlife sanctuaries, "
            "and heritage sites.\n\n"
            "⚠️ *Note: The live Gemini AI service is awaiting configuration with a `GEMINI_API_KEY`. "
            "Please add your `GEMINI_API_KEY` to the `.env` file to unlock dynamic AI responses for any custom query!*\n\n"
            "Popular recommendations you can explore in the meantime:\n"
            "• **Coorg & Chikmagalur**: Lush coffee plantations, mist-covered peaks, and eco-homestays.\n"
            "• **Kabini & Bandipur**: Premier wildlife safaris, elephant corridors, and responsible tiger reserves.\n"
            "• **Gokarna & Karwar**: Pristine beaches, coastal treks, and serene backwaters.\n"
            "• **Hampi & Badami**: UNESCO World Heritage architecture amidst boulder-strewn landscapes."
        )

    prompt = f"""{SYSTEM_PROMPT}

Language Requirement: Respond completely in {language}.

User Question:
{message}
"""

    model_name = settings.gemini_model or "gemini-3.8-flash"
    fallback_models = [model_name, "gemini-3.8-flash", "gemini-2.5-flash", "gemini-2.0-flash"]
    # Deduplicate while preserving order
    seen = set()
    models_to_try = [m for m in fallback_models if not (m in seen or seen.add(m))]

    last_error = None
    for model in models_to_try:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
            )
            if response and response.text:
                return response.text.strip()
        except Exception as exc:
            logger.warning("Error generating content with model %s: %s", model, exc)
            last_error = exc

    logger.error("All Gemini models failed: %s", last_error)
    return (
        f"🌿 I apologize, but I encountered a temporary issue connecting to the AI guide service ({last_error}). "
        "Please verify your API key and network connection, or try again shortly."
    )
