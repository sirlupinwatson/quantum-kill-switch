# Quantum Kill Switch (QKD Tandem)

Quantum Kill Switch (`qkd_tandem`) is a research and simulation package for **Quantum Key Distribution (QKD)** protocols with a sabotage-resistant kill switch mechanism.  
It provides tools to simulate BB84 key exchange, introduce adversarial tampering, and evaluate the performance of a kill switch strategy under attack.

---

## Features

- **BB84 Simulation**: Classical QKD protocol with basis reconciliation and error rate estimation.
- **Kill Switch Mechanism**: A sabotage circuit (`star_qft`) that arms when tampering or high error rates are detected.
- **Rolling QBER Analysis**: Visualize error rates over time with sliding windows.
- **Benchmarking**: Automatically saves plots to `benchmarks/` for reproducibility.
- **CLI Entry Point**: Run simulations directly from the command line with `qkd-run`.

---

## Installation

Clone the repo and install in editable mode:

```bash
git clone https://github.com/sirlupinwatson/quantum-kill-switch.git
cd quantum-kill-switch
pip install -e .
```

## Install directly from PyPi

```bash
pip install qkd_tandem
```

## Run a default simulation

```bash
qkd-run # Also with python -m qdk_tandem.cli.run
```

## Sweep attack rates

```bash
qkd-run --sweep
```

## Example output

```bash
BB84 QBER: 0.1176
Kill Switch QBER: 0.4824
```

## Development

- Python 3.9+ recommended

- Dependencies:  
  - qiskit
  - qiskit-aer
  - matplotlib
  - numpy

- Run tests with:

    pytest tests/

## New in v0.2.0: Trielliptic Commitments

This version introduces **trielliptic binding**, a 384‑bit digest that merges:

- 256‑bit QKD root
- 128‑bit Charly sabotage marker
- Metadata (timestamp + route)

The binding is computed with BLAKE3 (or BLAKE2b fallback) and used to derive AES‑256‑GCM encryption keys.  

- Packets now include:
  - `trielliptic_commit` section with root, marker, and binding
  - `metadata_b64` for reproducible verification
  - Automatic benchmark artifacts (`benchmarks/honest_packet.json`, `benchmarks/tampered_packet.json`)

Tests validate both honest and tampered paths, ensuring the kill‑switch activates under sabotage.

## Example

```bash
============================================= test session starts ==============================================
platform win32 -- Python 3.13.2, pytest-9.0.1, pluggy-1.6.0 -- \quantum-kill-switch\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: \quantum-kill-switch
configfile: pytest.ini
collected 8 items

tests\test_bb84.py::test_clean_low_qber PASSED                                                            [ 12%]
tests\test_bb84.py::test_tampered_ks_higher_qber PASSED                                                   [ 25%]
tests\test_trielliptic_digest.py::test_digest_with_blake3 PASSED                                          [ 37%] 
tests\test_trielliptic_digest.py::test_digest_fallback PASSED                                             [ 50%] 
tests\test_trielliptic_digest.py::test_honest_path PASSED                                                 [ 62%] 
tests\test_trielliptic_digest.py::test_tampered_path PASSED                                               [ 75%] 
tests\test_trielliptic_packet.py::test_honest_path PASSED                                                 [ 87%] 
tests\test_trielliptic_packet.py::test_charly_tampered PASSED                                             [100%] 

======================================== 8 passed in 489.08s (0:08:09) =========================================
```

### honest_packet.json

```json
{
  "qks_version": "0.2.0-trielliptic",
  "metadata_b64": "eyJ0aW1lc3RhbXAiOiAiMjAyNS0xMS0xNVQwNjoyMDowNC40MzMwMzcrMDA6MDAiLCAicm91dGUiOiBbImFsaWNlIiwgImhvbmVzdC1yZWxheSIsICJib2IiXX0=",
  "packet_id": "qks-2025-11-15T06:20:04Z-afffe39f",
  "timestamp": "2025-11-15T06:20:04.434684+00:00",
  "route": [
    "alice",
    "honest-relay",
    "bob"
  ],
  "trielliptic_commit": {
    "qkd_root": "256:8c2e2eaa418df37c86d17c1127a38786300134ca3a09a2669f90cf06a41a88f1",
    "charly_marker": "128:00000000000000000000000000000000",
    "final_binding": "384:f5a4ac27f5a4fabe49ad5ff57e251ebd1ba85526fdd83edb11cfade877063c5951800e896af4b56676073a8f10fdf4b0"
  },
  "payload_commit": "sha3-256:c2b672f8c5a02dd2106579f4ec252df061c345ae7ac39fa1b679efbd135fc8df",
  "payload_ciphertext_b64": "v99NQG3HnW3xU4/XC3ttM2ZfDk3f0m0+wNkb4Qq/foN/kN+BPr5x8pQ0XSUH31TcRdwDUJBHug==",
  "proof": null,
  "self_destruct_trigger": null,
  "signature": null
}
```

### tampeted_packed.json

```json
{
  "qks_version": "0.2.0-trielliptic",
  "metadata_b64": "eyJ0aW1lc3RhbXAiOiAiMjAyNS0xMS0xNVQwNjoyMDowNC40MzY3OTIrMDA6MDAiLCAicm91dGUiOiBbImFsaWNlIiwgInNuZWFreS1jaGFybHkiLCAiYm9iIl19",
  "packet_id": "qks-2025-11-15T06:20:04Z-97c43c80",
  "timestamp": "2025-11-15T06:20:04.436848+00:00",
  "route": [
    "alice",
    "sneaky-charly",
    "bob"
  ],
  "trielliptic_commit": {
    "qkd_root": "256:928b3ae6880b254cf01b7332d67757ed6a895bc1086bf855484b5c5686790cc6",
    "charly_marker": "128:4c7a2ef4ff645ed770535dd0b9d1421a",
    "final_binding": "384:bbf8423280f5b38d4567fd5ff4394374a125121feb2dc624746d273f030e3854b62bd9ddcf4e6c59f3b137910ed1466a"
  },
  "payload_commit": "sha3-256:0991ea576e72d93495ddef42433bace820c408179d8ffed0923536adaac5c2d6",
  "payload_ciphertext_b64": "72yvC2RzGrCWdyQLA6sYJUJ6aUKGZxFKSrFFPogpsmDnS7LZWlScrfHA73/1xzlg0YI=",
  "proof": null,
  "self_destruct_trigger": "charly_detected",
  "signature": null
}
```

## 📜 License

MITx License. See [LICENSE](LICENSE) for details.
