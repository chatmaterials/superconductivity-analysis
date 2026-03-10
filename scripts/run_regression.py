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
    phonons = run_json("scripts/analyze_phonon_modes.py", "fixtures/phonon/phonon_modes.dat", "--json")
    ensure(phonons["soft_mode_count"] == 1, "superconductivity-analysis should detect one soft mode in the fixture")
    tc = run_json("scripts/estimate_tc.py", "--alpha2f-path", "fixtures/alpha2f/alpha2f.dat", "--mu-star", "0.10", "--json")
    ensure(tc["tc_K"] > 0, "superconductivity-analysis should estimate a positive Tc")
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
    finally:
        shutil.rmtree(temp_dir)
    print("superconductivity-analysis regression passed")


if __name__ == "__main__":
    main()
