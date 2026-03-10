# superconductivity-analysis

[![CI](https://img.shields.io/github/actions/workflow/status/chatmaterials/superconductivity-analysis/ci.yml?branch=main&label=CI)](https://github.com/chatmaterials/superconductivity-analysis/actions/workflows/ci.yml) [![Release](https://img.shields.io/github/v/release/chatmaterials/superconductivity-analysis?display_name=tag)](https://github.com/chatmaterials/superconductivity-analysis/releases)

Standalone skill for superconductivity-relevant DFT result analysis.

## Install

```bash
npx skills add chatmaterials/superconductivity-analysis -g -y
```

## Local Validation

```bash
python3 -m py_compile scripts/*.py
npx skills add . --list
python3 scripts/analyze_alpha2f.py fixtures/alpha2f/alpha2f.dat --json
python3 scripts/analyze_phonon_modes.py fixtures/phonon/phonon_modes.dat --json
python3 scripts/estimate_tc.py --alpha2f-path fixtures/alpha2f/alpha2f.dat --mu-star 0.10 --json
python3 scripts/export_superconductivity_report.py --alpha2f-path fixtures/alpha2f/alpha2f.dat --phonon-path fixtures/phonon/phonon_modes.dat --mu-star 0.10
python3 scripts/run_regression.py
```
