---
name: "superconductivity-analysis"
description: "Use when the task is to analyze superconductivity-relevant quantities from DFT or Eliashberg-style outputs, including electron-phonon coupling summaries, logarithmic phonon frequency estimates, soft-mode checks, Allen-Dynes Tc estimates, and compact markdown reports from finished calculations."
---

# Superconductivity Analysis

Use this skill for superconductivity-oriented post-processing rather than generic workflow setup.

## When to use

- summarize electron-phonon coupling from an `alpha^2F`-like spectrum
- estimate `lambda` and `omega_log`
- check whether a phonon mode set contains soft or imaginary modes
- estimate a simple Allen-Dynes `Tc`
- write a compact superconductivity-analysis report from existing data

## Use the bundled helpers

- `scripts/analyze_alpha2f.py`
  Estimate `lambda` and `omega_log` from an `alpha^2F` spectrum.
- `scripts/analyze_phonon_modes.py`
  Summarize phonon-mode stability and soft-mode counts.
- `scripts/estimate_tc.py`
  Estimate `Tc` from `lambda`, `omega_log`, and `mu*`.
- `scripts/export_superconductivity_report.py`
  Export a markdown superconductivity-analysis report.

## Guardrails

- Treat the resulting `Tc` as a compact estimate, not a full superconductivity prediction workflow.
- Be explicit about the chosen `mu*`.
- Distinguish soft modes from fully imaginary-mode instabilities.
