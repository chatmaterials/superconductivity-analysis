#!/usr/bin/env python3

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=True)


def run_json(*args: str):
    return json.loads(run(*args).stdout)


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    epc = run_json("scripts/analyze_alpha2f.py", "fixtures/alpha2f/alpha2f.dat", "--json")
    ensure(epc["lambda_ep"] > 0.3, "superconductivity-analysis should estimate a finite coupling constant")
    ensure(epc["coupling_regime"] == "weak-coupling", "superconductivity-analysis should classify the reference coupling regime")
    phonons = run_json("scripts/analyze_phonon_modes.py", "fixtures/phonon/phonon_modes.dat", "--json")
    ensure(phonons["soft_mode_count"] == 1, "superconductivity-analysis should detect one soft mode in the fixture")
    ensure(phonons["stability_class"] == "softened", "superconductivity-analysis should classify the reference phonon set")
    tc = run_json("scripts/estimate_tc.py", "--alpha2f-path", "fixtures/alpha2f/alpha2f.dat", "--mu-star", "0.10", "--json")
    ensure(tc["tc_K"] > 0, "superconductivity-analysis should estimate a positive Tc")
    ensure(tc["tc_class"] == "low-Tc-like", "superconductivity-analysis should classify the reference Tc scale")
    ranked = run_json(
        "scripts/compare_superconducting_candidates.py",
        "fixtures",
        "fixtures/candidates/unstable-strong",
        "--mu-star",
        "0.10",
        "--target-tc",
        "0.5",
        "--json",
    )
    ensure(ranked["best_case"] == "fixtures", "superconductivity-analysis should rank the softened but stable fixture ahead of the unstable candidate")
    temp_dir = Path(tempfile.mkdtemp(prefix="superconductivity-analysis-report-"))
    try:
        report_path = Path(
            run(
                "scripts/export_superconductivity_report.py",
                "--alpha2f-path",
                "fixtures/alpha2f/alpha2f.dat",
                "--phonon-path",
                "fixtures/phonon/phonon_modes.dat",
                "--mu-star",
                "0.10",
                "--output",
                str(temp_dir / "SUPERCONDUCTIVITY_REPORT.md"),
            ).stdout.strip()
        )
        report_text = report_path.read_text()
        ensure("# Superconductivity Analysis Report" in report_text, "superconductivity report should have a heading")
        ensure("## Electron-Phonon Coupling" in report_text and "## Tc Estimate" in report_text, "superconductivity report should include EPC and Tc sections")
        ensure("## Screening Note" in report_text, "superconductivity report should include a screening note")
    finally:
        shutil.rmtree(temp_dir)
    print("superconductivity-analysis regression passed")


if __name__ == "__main__":
    main()
