#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from analyze_alpha2f import analyze as analyze_alpha2f


def allen_dynes_tc(lambda_ep: float, omega_log_K: float, mu_star: float) -> float:
    denominator = lambda_ep - mu_star * (1.0 + 0.62 * lambda_ep)
    if denominator <= 0:
        raise SystemExit("Allen-Dynes denominator is non-positive; check lambda and mu*")
    exponent = -1.04 * (1.0 + lambda_ep) / denominator
    return (omega_log_K / 1.2) * math.exp(exponent)


def analyze(alpha2f_path: Path, mu_star: float) -> dict[str, object]:
    epc = analyze_alpha2f(alpha2f_path)
    tc = allen_dynes_tc(epc["lambda_ep"], epc["omega_log_K"], mu_star)
    if tc >= 20.0:
        tc_class = "high-Tc-like"
    elif tc >= 5.0:
        tc_class = "moderate-Tc-like"
    elif tc > 0.0:
        tc_class = "low-Tc-like"
    else:
        tc_class = "non-superconducting-like"
    return {
        "path": str(alpha2f_path),
        "lambda_ep": epc["lambda_ep"],
        "omega_log_K": epc["omega_log_K"],
        "mu_star": mu_star,
        "tc_K": tc,
        "tc_class": tc_class,
        "screening_tc_K": tc,
        "observations": ["Allen-Dynes Tc estimate computed from lambda, omega_log, and mu*."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate Tc from an alpha^2F spectrum.")
    parser.add_argument("--alpha2f-path", required=True)
    parser.add_argument("--mu-star", type=float, default=0.10)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = analyze(Path(args.alpha2f_path).expanduser().resolve(), args.mu_star)
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
