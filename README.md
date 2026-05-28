# CCT-Open

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20427785.svg)](https://doi.org/10.5281/zenodo.20427785)
[![PyPI version](https://img.shields.io/badge/pypi-coming%20soon-lightgrey)](https://pypi.org)

Open source Python library implementing **Consolidation Control Theory (CCT)**: a computational framework that predicts reward memory encoding probability from receptor-level neurochemical input data.

CCT-Open accepts two input types:

- **CNS drug candidates** — receptor binding affinity profiles, returning addiction liability risk scores and encoding probability estimates
- **BCI stimulation protocols** — neurostimulation parameters, returning addiction encoding risk predictions for stimulation protocols

The full theoretical framework is publicly archived at [https://doi.org/10.5281/zenodo.20427785](https://doi.org/10.5281/zenodo.20427785).

---

## Overview

CCT-Open implements a three-layer computational architecture:

| Layer | Module | Input | Output |
|---|---|---|---|
| 1 | Receptor Binding Input | Binding affinity profile (Ki/IC50 values) | Normalised receptor occupancy vector |
| 2 | Receptor-to-Axis Transfer | Receptor occupancy vector | Neural axis activation scores |
| 3 | CCT Encoding | Axis activation scores | Encoding probability + risk class |

The GATE extension accepts BCI stimulation parameters as input and routes them through the same encoding probability engine, enabling addiction risk assessment for neurostimulation protocols.

---

## Installation

```bash
pip install cct-open
```

PyPI release will be available on project completion. Until then, install from source:

```bash
git clone https://github.com/Amunraptah/cct-open.git
cd cct-open
pip install -e .
```

---

## Quick Start

```python
from cct_open import CCTModel

model = CCTModel()

# CNS drug screening
binding_profile = {
    "DAT": 45.2,
    "NET": 180.0,
    "SERT": 920.0,
    "D2": 310.0,
    "MOR": 1200.0,
}

result = model.predict(binding_profile)
print(result.encoding_probability)  # float [0, 1]
print(result.risk_class)            # "low" | "moderate" | "high"
```

```python
from cct_open.gate import GATEModel

gate = GATEModel()

# BCI stimulation safety
stimulation_params = {
    "target_region": "nucleus_accumbens",
    "frequency_hz": 130,
    "amplitude_ma": 2.5,
    "pulse_width_us": 90,
    "session_duration_min": 60,
}

result = gate.predict(stimulation_params)
print(result.encoding_probability)
print(result.risk_class)
```

---

## Project Structure

```
cct-open/
├── cct_open/
│   ├── __init__.py         # Package entry point
│   ├── core.py             # Three-layer CCT model
│   ├── receptor.py         # Layer 1: receptor binding input module
│   ├── transfer.py         # Layer 2: receptor-to-axis transfer function
│   ├── encoding.py         # Layer 3: encoding probability computation
│   ├── gate.py             # GATE: BCI stimulation safety module
│   └── utils.py            # Shared utilities and validation
├── docs/
│   ├── cns_workflow.md     # Tutorial: CNS drug screening workflow
│   └── bci_workflow.md     # Tutorial: BCI safety workflow
├── tests/
│   ├── test_core.py
│   ├── test_gate.py
│   └── test_validation.py
├── requirements.txt
├── setup.py
└── README.md
```

---

## Validation

CCT-Open is validated against a curated reference set of compounds with established addiction liability classifications drawn from DEA Schedule classifications cross-referenced with receptor binding profiles from ChEMBL. Validation methodology, compound list, and full reproducibility materials are documented in the [validation report](docs/validation_report.md) (published on project completion).

---

## Theoretical Framework

CCT models the molecular consolidation window during which drug or stimulation experiences consolidate into durable motivational memories. The mathematical foundations are formalised in the archived preprint:

> Olutogun, E. (2025). Consolidation Control Theory: A Computational Framework for Reward Memory Encoding Probability. Zenodo. https://doi.org/10.5281/zenodo.20427785

---

## Funding

CCT-Open is developed with support from the NGI Zero Commons Fund, a grant programme funded by the European Commission's Next Generation Internet initiative.

---

## License

Apache 2.0. See [LICENSE](LICENSE) for full terms.

---

## Citation

```bibtex
@software{cct_open,
  author  = {Olutogun, Eniola},
  title   = {CCT-Open: Open Source Computational Framework for Addiction Liability Prediction},
  year    = {2025},
  url     = {https://github.com/Amunraptah/cct-open},
  license = {Apache-2.0}
}
```
