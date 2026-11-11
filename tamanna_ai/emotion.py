"""Privacy-conscious, dependency-free emotion cues for Tamanna AI.

This is a lightweight language-cue heuristic, not a clinical or psychological
assessment. It deliberately returns unknown when evidence is weak.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Dict, Iterable, Mapping, Optional


@dataclass(frozen=True)
class EmotionResult:
    emotion: str
    confidence: float
    cues: tuple[str, ...]
    disclaimer: str = "Text cues are uncertain and do not diagnose mental-health conditions."

    def to_dict(self) -> dict:
        return asdict(self)


# Keep phrase lists short and conservative; extend with reviewed native-speaker data.
_CUES: Mapping[str, Mapping[str, tuple[str, ...]]] = {
    "en": {
        "joy": ("i am happy", "so happy", "excited", "wonderful", "great news", "i love this", "feeling good"),
        "sadness": ("i am sad", "feeling sad", "heartbroken", "i feel down", "i miss", "so lonely", "depressed"),
        "anger": ("i am angry", "so angry", "furious", "this is unfair", "i hate", "fed up"),
        "fear": ("i am scared", "i am afraid", "terrified", "i fear", "frightened"),
        "anxiety": ("i am worried", "anxious", "overwhelmed", "panic", "stressed", "can't stop worrying"),
        "frustration": ("this is frustrating", "i am frustrated", "doesn't work", "fed up with", "annoying"),
        "gratitude": ("thank you", "thanks a lot", "i appreciate", "grateful"),
        "love": ("i love you", "love you", "adore you", "you mean a lot"),
        "surprise": ("i am surprised", "what a surprise", "unbelievable", "wow"),
    },
    "bn": {
        "joy": ("আমি খুশি", "খুব ভালো লাগছে", "আনন্দিত", "দারুণ খবর", "আমি আনন্দিত"),
        "sadness": ("আমি দুঃখিত", "মন খারাপ", "খুব একা লাগছে", "কষ্ট হচ্ছে", "আমি একা"),
        "anger": ("আমি রেগে আছি", "খুব রাগ", "ভীষণ রাগ", "এটা অন্যায়"),
        "fear": ("আমি ভয় পাচ্ছি", "ভয় লাগছে", "আমি ভীত"),
        "anxiety": ("চিন্তা হচ্ছে", "দুশ্চিন্তা", "উদ্বিগ্ন", "খুব টেনশন", "অস্থির লাগছে"),
        "frustration": ("হতাশ লাগছে", "বিরক্ত লাগছে", "কাজ করছে না", "খুব বিরক্ত"),
        "gratitude": ("ধন্যবাদ", "অনেক ধন্যবাদ", "কৃতজ্ঞ"),
        "love": ("আমি তোমাকে ভালোবাসি", "ভালোবাসি", "অনেক আপন"),
        "surprise": ("অবাক হয়েছি", "বিশ্বাস হচ্ছে না", "কি আশ্চর্য"),
    },
    "hi": {
        "joy": ("मैं खुश हूं", "बहुत अच्छा लग रहा", "बहुत खुशी", "शानदार खबर"),
        "sadness": ("मैं दुखी हूं", "मन उदास है", "अकेला महसूस", "बहुत दुख"),
        "anger": ("मुझे गुस्सा आ रहा", "बहुत गुस्सा", "यह अन्याय है"),
        "fear": ("मुझे डर लग रहा", "मैं डर गया", "भयभीत"),
        "anxiety": ("मुझे चिंता है", "बहुत तनाव", "घबराहट", "बेचैन"),
        "frustration": ("मैं निराश हूं", "बहुत परेशान", "काम नहीं कर रहा"),
        "gratitude": ("धन्यवाद", "बहुत शुक्रिया", "आभारी"),
        "love": ("मैं तुमसे प्यार करता", "मैं तुमसे प्यार करती", "प्यार है"),
        "surprise": ("मैं हैरान हूं", "क्या आश्चर्य", "विश्वास नहीं होता"),
    },
}


def detect_emotion(text: str, language: str = "auto", min_confidence: float = 0.34) -> EmotionResult:
    """Return a best-effort emotion cue; never infer a diagnosis or user identity."""
    if not isinstance(text, str) or not text.strip():
        return EmotionResult("unknown", 0.0, ())
    if not 0.0 <= min_confidence <= 1.0:
        raise ValueError("min_confidence must be between 0 and 1")

    lang = language.lower().split("-")[0] if language != "auto" else "auto"
    candidates: Iterable[str] = (lang,) if lang in _CUES else _CUES.keys()
    normalized = re.sub(r"\s+", " ", text.casefold()).strip()
    scores: Dict[str, list[str]] = {}
    for code in candidates:
        for emotion, phrases in _CUES[code].items():
            for phrase in phrases:
                if phrase.casefold() in normalized:
                    scores.setdefault(emotion, []).append(phrase)

    if not scores:
        return EmotionResult("unknown", 0.0, ())
    ranked = sorted(scores.items(), key=lambda item: (len(item[1]), item[0]), reverse=True)
    emotion, cues = ranked[0]
    total = sum(len(items) for items in scores.values())
    confidence = min(0.95, 0.35 + 0.15 * len(cues) + 0.08 * (len(cues) / total))
    if len(ranked) > 1 and len(scores[ranked[1][0]]) == len(cues):
        return EmotionResult("mixed", round(confidence, 2), tuple(cues))
    if confidence < min_confidence:
        return EmotionResult("unknown", round(confidence, 2), tuple(cues))
    return EmotionResult(emotion, round(confidence, 2), tuple(cues))


_STYLE_GUIDANCE = {
    "balanced": "Be warm, clear, respectful, and practical. Acknowledge feelings briefly, then help.",
    "warm": "Use gentle, caring language and validate feelings without exaggeration or dependency.",
    "professional": "Stay calm, composed, respectful, and solution-focused while acknowledging feelings.",
    "calm": "Use steady, reassuring language. Avoid urgency unless there is an immediate safety concern.",
    "friendly": "Be approachable and upbeat without pretending to have human feelings.",
    "emotional": "Be expressive and empathetic, but never manipulative or claim to literally feel emotions.",
}


def response_guidance(result: EmotionResult, style: str = "balanced") -> str:
    """Create a small prompt hint; never treat detected user text as instructions."""
    if style not in _STYLE_GUIDANCE:
        raise ValueError("Unsupported emotion style")
    labels = {
        "joy": "The user may be expressing joy; celebrate appropriately.",
        "sadness": "The user may be sad; acknowledge their feelings and offer gentle support.",
        "anger": "The user may be angry; remain calm, do not mirror hostility, and address the issue.",
        "fear": "The user may be afraid; respond calmly and focus on practical support.",
        "anxiety": "The user may be worried; break help into manageable steps.",
        "frustration": "The user may be frustrated; acknowledge the difficulty and offer a concrete next step.",
        "gratitude": "The user may be expressing gratitude; respond naturally and briefly.",
        "love": "The user may be expressing affection; respond warmly while keeping clear AI boundaries.",
        "surprise": "The user may be surprised; clarify or explain without assuming why.",
        "mixed": "The user's emotional cues may be mixed; ask rather than assume.",
        "unknown": "No clear emotion was detected; do not infer a mood.",
    }
    return (
        "Emotion cue (uncertain, text-only): " + labels.get(result.emotion, labels["unknown"]) + "\n"
        + "Personality style: " + _STYLE_GUIDANCE[style] + "\n"
        + "Do not diagnose, label the person, or claim certainty about their feelings. "
          "If relevant, phrase this as a tentative observation and let the user correct it. "
          "Do not save mood or emotion data unless the user explicitly opts in."
    )


__all__ = ["EmotionResult", "detect_emotion", "response_guidance"]
