import json
import os
import pytest
import hashlib
from base64 import b64decode
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from qkd_tandem.trielliptic_packet import (
    trielliptic_digest,
    generate_trielliptic_packet,
    verify_and_self_destruct,
)

def test_digest_with_blake3():
    import blake3
    data = b"test-data"
    digest = trielliptic_digest(data)
    expected = blake3.blake3(data).digest(length=48)
    assert digest == expected
    assert len(digest) == 48

def test_digest_fallback(monkeypatch):
    monkeypatch.setitem(__import__('sys').modules, 'blake3', None)
    data = b"test-data"
    digest = trielliptic_digest(data)
    expected = hashlib.blake2b(data, digest_size=48).digest()
    assert digest == expected
    assert len(digest) == 48

@pytest.mark.slow
def test_honest_path():
    payload = b"Secret message for Bob only"
    packet = generate_trielliptic_packet(
        payload=payload,
        route=["alice", "honest-relay", "bob"],
        charly_tampered=False
    )

    # Save packet to benchmarks/honest_packet.json
    os.makedirs("benchmarks", exist_ok=True)
    with open("benchmarks/honest_packet.json", "w") as f:
        json.dump(packet, f, indent=2)

    # Verify packet integrity
    assert verify_and_self_destruct(packet) is True

    # --- Automatic decryption check ---
    commit = packet["trielliptic_commit"]
    final_binding = bytes.fromhex(commit["final_binding"].split(":", 1)[1])
    metadata = b64decode(packet["metadata_b64"])

    key = hashlib.sha3_256(final_binding).digest()
    aesgcm = AESGCM(key)
    raw_ct = b64decode(packet["payload_ciphertext_b64"])
    nonce, ciphertext = raw_ct[:12], raw_ct[12:]
    decrypted = aesgcm.decrypt(nonce, ciphertext, metadata)

    # Assert decrypted payload matches original
    assert decrypted == payload

def test_tampered_path():
    payload = b"I will never reach Bob"
    packet = generate_trielliptic_packet(
        payload=payload,
        route=["alice", "sneaky-charly", "bob"],
        charly_tampered=True
    )

    # Save tampered packet to benchmarks/tampered_packet.json
    os.makedirs("benchmarks", exist_ok=True)
    with open("benchmarks/tampered_packet.json", "w") as f:
        json.dump(packet, f, indent=2)

    # Verify that kill-switch triggers
    assert verify_and_self_destruct(packet) is False

    # Ensure self_destruct_trigger is set
    assert packet["self_destruct_trigger"] == "charly_detected"
