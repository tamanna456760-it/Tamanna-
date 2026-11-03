import hashlib
import hmac

from tamanna_ai.integrations.central_server import _canonical


def test_protocol_canonical_message_includes_body_digest():
    body = b'{"agent_id":"tamanna-ai"}'
    canonical = _canonical("POST", "/protocol/v1/report", "1700000000", "nonce_1234567890123456", body)
    expected = "\n".join((
        "1",
        "POST",
        "/protocol/v1/report",
        "1700000000",
        "nonce_1234567890123456",
        hashlib.sha256(body).hexdigest(),
    )).encode()
    assert canonical == expected


def test_protocol_hmac_is_sha256():
    secret = "s" * 64
    body = b'{}'
    canonical = _canonical("POST", "/protocol/v1/report", "1700000000", "nonce_1234567890123456", body)
    signature = hmac.new(secret.encode(), canonical, hashlib.sha256).hexdigest()
    assert len(signature) == 64
