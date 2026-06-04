# test/test_ai.py

from ai import ai_reply

def test_hello():
    assert ai_reply("hello") == "Hi!"