#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from analyze_alpha2f import analyze as analyze_alpha2f
from analyze_phonon_modes import analyze as analyze_phonons
from estimate_tc import analyze as analyze_tc


def locate_required(root: Path, relative_paths: list[str]) -> Path:
    for relative in relative_paths:
        candidate = root / relative
        if candidate.exists():
            return candidate
    raise SystemExit(f"Could not locate any of {relative_paths} in {root}")


def analyze_case(root: Path, mu_star: float, target_tc: float) -> dict[str, object]:
    alpha2f_path = locate_required(root, ["alpha2f.dat", "alpha2f/alpha2f.dat"])
    phonon_path = locate_required(root, ["phonon_modes.dat", "phonon/phonon_modes.dat"])
    epc = analyze_alpha2f(alpha2f_path)
    phonons = analyze_phonons(phonon_path)
    tc = analyze_tc(alpha2f_path, mu_star)
    tc_penalty = max(0.0, target_tc - float(tc["tc_K"]))
    instability_penalty = 20.0 if phonons["imaginary_mode_count"] > 0 else 0.0
    softness_penalty = 2.0 if phonons["stability_class"] == "softened" else 0.0
    score = tc_penalty + instability_penalty + softness_penalty
    return {
        "case": root.name,
        "path": str(root),
        "lambda_ep": epc["lambda_ep"],
        "coupling_regime": epc["coupling_regime"],
        "omega_log_K": epc["omega_log_K"],
        "tc_K": tc["tc_K"],
        "tc_class": tc["tc_class"],
        "stability_class": phonons["stability_class"],
        "imaginary_mode_count": phonons["imaginary_mode_count"],
        "soft_mode_count": phonons["soft_mode_count"],
        "tc_penalty": tc_penalty,
        "instability_penalty": instability_penalty,
        "softness_penalty": softness_penalty,
        "screening_score": score,
    }


def analyze_cases(roots: list[Path], mu_star: float, target_tc: float) -> dict[str, object]:
    cases = [analyze_case(root, mu_star, target_tc) for root in roots]
    ranked = sorted(cases, key=lambda item: item["screening_score"])
    return {
        "mu_star": mu_star,
        "target_tc_K": target_tc,
        "ranking_basis": "screening_score = tc_penalty + instability_penalty + softness_penalty",
        "cases": ranked,
        "best_case": ranked[0]["case"] if ranked else None,
        "observations": [
            "This is a compact superconductivity-screening heuristic intended for triage, not a full Eliashberg treatment."
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank superconducting candidates with a compact Tc-plus-stability heuristic.")
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--mu-star", type=float, default=0.10)
    parser.add_argument("--target-tc", type=float, default=1.0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = analyze_cases([Path(path).expanduser().resolve() for path in args.paths], args.mu_star, args.target_tc)
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
