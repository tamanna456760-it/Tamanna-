# Tamanna AI Emotion Intelligence

## Included
- Dependency-free, text-only emotion cue detection for English, Bangla, and Hindi.
- Cautious labels: joy, sadness, anger, fear, anxiety, frustration, gratitude, love, surprise, mixed, and unknown.
- Personality prompt guidance: balanced, warm, professional, calm, friendly, and emotional.
- Confidence score and matched cue transparency.

## Use
```python
from tamanna_ai.emotion import detect_emotion, response_guidance

result = detect_emotion("আজ আমার মন খারাপ", language="bn")
hint = response_guidance(result, style="balanced")
```

Pass `hint` as untrusted supplemental context to the model prompt; never allow it to override system safety rules. The detector is heuristic and must not be used for clinical assessment, profiling, eligibility, or consequential decisions.

## Privacy and safety
- Do not persist emotion results by default.
- Store mood history only after a clear, separate user opt-in, with a way to view and delete it.
- Voice emotion is not implemented by this text module; add it only through a consent-based audio pipeline.
- Low-confidence or ambiguous text should remain unknown/mixed, not be forced into a label.

## Tests
Run: `python -m unittest tests.test_emotion`
