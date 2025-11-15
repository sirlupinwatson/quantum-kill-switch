# qkd_tandem/tests/test_trielliptic_packet.py
import json
from qkd_tandem.trielliptic_packet import generate_trielliptic_packet, verify_and_self_destruct

def test_honest_path():
    payload = b"Secret message for Bob only"
    packet = generate_trielliptic_packet(
        payload=payload,
        route=["alice", "honest-relay", "bob"],
        charly_tampered=False
    )
    # Print pretty JSON once so you can see the format
    print("\nHonest packet:")
    print(json.dumps(packet, indent=2))
    
    assert verify_and_self_destruct(packet) is True
    print("Honest path: SUCCESS")

def test_charly_tampered():
    payload = b"I will never reach Bob"
    packet = generate_trielliptic_packet(
        payload=payload,
        route=["alice", "sneaky-charly", "bob"],
        charly_tampered=True
    )
    print("\nCharly-tampered packet generated (marker non-zero)...")
    
    assert verify_and_self_destruct(packet) is False
    print("Charly path: KILL-SWITCH ACTIVATED - payload nuked")