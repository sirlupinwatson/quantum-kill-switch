# qkd_tandem/trielliptic_packet.py
import hashlib
import secrets
import json
from datetime import datetime, timezone
from base64 import b64encode, b64decode
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
# Optional: from .bb84_tandem import TandemQKD  # Real integration hook

def trielliptic_digest(data: bytes) -> bytes:
    """
    Compute a 384-bit digest using BLAKE3 if available, else fall back to BLAKE2b.
    """
    try:
        import blake3
        return blake3.blake3(data).digest(length=48)
    except ImportError:
        return hashlib.blake2b(data, digest_size=48).digest()

def generate_trielliptic_packet(
    payload: bytes,
    route: list[str],
    charly_tampered: bool = False,
    qkd_seed: bytes = None
) -> dict:
    """
    Generate a self-destructing quantum packet with trielliptic commitments.
    """
    # 1. 256-bit QKD root (real: from TandemQKD; sim: random)
    qkd_root = qkd_seed or secrets.token_bytes(32)

    # 2. 128-bit Charly marker (non-zero if tampered)
    charly_marker = secrets.token_bytes(16) if charly_tampered else bytes(16)

    # 3. Metadata for binding
    metadata = json.dumps({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "route": route
    }).encode()

    # 4. 384-bit trielliptic binding
    binding_input = qkd_root + charly_marker + metadata
    final_binding = trielliptic_digest(binding_input)

    # 5. Encrypt payload (AES-256-GCM, key-derived from binding)
    key = hashlib.sha3_256(final_binding).digest()
    aesgcm = AESGCM(key)
    nonce = secrets.token_bytes(12)
    ciphertext = aesgcm.encrypt(nonce, payload, metadata)

    # 6. Assemble JSON packet
    packet = {
        "qks_version": "0.2.0-trielliptic",
        "metadata_b64": b64encode(metadata).decode(),
        "packet_id": f"qks-{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')}Z-{secrets.token_hex(4)}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "route": route,
        "trielliptic_commit": {
            "qkd_root": f"256:{qkd_root.hex()}",
            "charly_marker": f"128:{charly_marker.hex()}",
            "final_binding": f"384:{final_binding.hex()}"
        },
        "payload_commit": f"sha3-256:{hashlib.sha3_256(payload).hexdigest()}",
        "payload_ciphertext_b64": b64encode(nonce + ciphertext).decode(),
        "proof": None,  # Future: ZK proof object
        "self_destruct_trigger": "charly_detected" if charly_tampered and any(b != 0 for b in charly_marker) else None,
        "signature": None  # Future: Ed448 PQ sig
    }
    return packet

def verify_and_self_destruct(packet: dict) -> bool:
    """
    Validate packet at destination. Returns True if honest; else triggers destruct.
    """
    try:
        commit = packet["trielliptic_commit"]
        qkd_root = bytes.fromhex(commit["qkd_root"].split(":", 1)[1])
        charly_marker = bytes.fromhex(commit["charly_marker"].split(":", 1)[1])
        final_binding = bytes.fromhex(commit["final_binding"].split(":", 1)[1])

        metadata = json.dumps({
            "timestamp": packet["timestamp"],
            "route": packet["route"]
        }).encode()

        metadata = b64decode(packet["metadata_b64"])
        expected_binding = trielliptic_digest(qkd_root + charly_marker + metadata)

        if final_binding != expected_binding or any(b != 0 for b in charly_marker):
            print("QUANTUM KILL-SWITCH ACTIVATED: Sneaky Charly detected! Payload nuked.")
            packet["self_destruct_trigger"] = "charly_detected"
            return False

        # Decrypt & verify payload (for honest path)
        key = hashlib.sha3_256(final_binding).digest()
        aesgcm = AESGCM(key)
        raw_ct = b64decode(packet["payload_ciphertext_b64"])
        nonce, ciphertext = raw_ct[:12], raw_ct[12:]
        decrypted = aesgcm.decrypt(nonce, ciphertext, metadata)
        expected_commit = hashlib.sha3_256(decrypted).hexdigest()
        if expected_commit != packet["payload_commit"].split(":", 1)[1]:
            raise ValueError("Payload tampered!")

        print("Honest packet verified. Delivering payload.")
        return True
    except Exception as e:
        print(f"Verification failed: {e}. Kill-switch engaged.")
        return False