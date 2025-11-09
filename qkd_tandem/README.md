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

## 📜 License

MITx License. See [LICENSE](LICENSE) for details.
