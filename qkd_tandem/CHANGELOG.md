# Changelog

## [0.2.0] - 2025-11-15
### Added
- Trielliptic binding (384‑bit) combining 256‑bit QKD root + 128‑bit Charly marker + metadata.
- `metadata_b64` field for reproducible verification.
- AES‑256‑GCM encryption keyed from trielliptic digest.
- Honest and tampered packet tests with automatic benchmark JSON output.
- Pytest markers for slow tests.

### Changed
- Updated `pyproject.toml` to version 0.2.0.
- Updated README.md with trielliptic commitments section.
