#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from analyze_alpha2f import analyze as analyze_alpha2f
from analyze_phonon_modes import analyze as analyze_phonons
from analyze_tc_sensitivity import analyze as analyze_tc_sensitivity
from estimate_tc import analyze as analyze_tc


def locate_required(root: Path, relative_paths: list[str]) -> Path:
    for relative in relative_paths:
        candidate = root / relative
        if candidate.exists():
            return candidate
    raise SystemExit(f"Could not locate any of {relative_paths} in {root}")


def analyze_case(root: Path, mu_star: float, target_tc: float, mode: str) -> dict[str, object]:
    alpha2f_path = locate_required(root, ["alpha2f.dat", "alpha2f/alpha2f.dat"])
    phonon_path = locate_required(root, ["phonon_modes.dat", "phonon/phonon_modes.dat"])
    epc = analyze_alpha2f(alpha2f_path)
    phonons = analyze_phonons(phonon_path)
    tc = analyze_tc(alpha2f_path, mu_star)
    sensitivity = analyze_tc_sensitivity(alpha2f_path, 0.08, 0.15, 0.01)
    tc_penalty = max(0.0, target_tc - float(tc["tc_K"]))
    instability_penalty = 20.0 if phonons["imaginary_mode_count"] > 0 else 0.0
    softness_penalty = 2.0 if phonons["stability_class"] == "softened" else 0.0
    robustness_penalty = max(0.0, 1.0 - float(sensitivity["tc_min_K"]))
    screening_tc = float(tc["tc_K"])
    if phonons["stability_class"] == "softened":
        screening_tc *= 0.85
    elif phonons["stability_class"] == "unstable":
        screening_tc = 0.0
    if mode == "high-tc":
        score = -0.1 * screening_tc + 0.5 * instability_penalty + 0.1 * softness_penalty + 0.1 * robustness_penalty
    elif mode == "robust":
        score = 1.0 * tc_penalty + 1.5 * instability_penalty + 1.0 * softness_penalty + 1.5 * robustness_penalty
    elif mode == "stable":
        score = 0.5 * tc_penalty + 2.0 * instability_penalty + 1.5 * softness_penalty + 0.5 * robustness_penalty
    else:
        score = tc_penalty + instability_penalty + softness_penalty + robustness_penalty
    return {
        "case": root.name,
        "path": str(root),
        "lambda_ep": epc["lambda_ep"],
        "coupling_regime": epc["coupling_regime"],
        "omega_log_K": epc["omega_log_K"],
        "tc_K": tc["tc_K"],
        "screening_tc_K": screening_tc,
        "tc_class": tc["tc_class"],
        "tc_min_K": sensitivity["tc_min_K"],
        "tc_max_K": sensitivity["tc_max_K"],
        "tc_robustness_class": sensitivity["robustness_class"],
        "stability_class": phonons["stability_class"],
        "imaginary_mode_count": phonons["imaginary_mode_count"],
        "soft_mode_count": phonons["soft_mode_count"],
        "tc_penalty": tc_penalty,
        "instability_penalty": instability_penalty,
        "softness_penalty": softness_penalty,
        "robustness_penalty": robustness_penalty,
        "screening_score": score,
    }


def analyze_cases(roots: list[Path], mu_star: float, target_tc: float, mode: str) -> dict[str, object]:
    cases = [analyze_case(root, mu_star, target_tc, mode) for root in roots]
    ranked = sorted(cases, key=lambda item: item["screening_score"])
    return {
        "mu_star": mu_star,
        "target_tc_K": target_tc,
        "mode": mode,
        "ranking_basis": "screening_score = weighted(tc_penalty, instability_penalty, softness_penalty, robustness_penalty)",
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
    parser.add_argument("--mode", choices=["balanced", "high-tc", "robust", "stable"], default="balanced")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = analyze_cases([Path(path).expanduser().resolve() for path in args.paths], args.mu_star, args.target_tc, args.mode)
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
