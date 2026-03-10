#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from estimate_tc import analyze as analyze_tc


def frange(start: float, stop: float, step: float) -> list[float]:
    values = []
    current = start
    while current <= stop + 1e-12:
        values.append(round(current, 10))
        current += step
    return values


def analyze(alpha2f_path: Path, mu_min: float, mu_max: float, mu_step: float) -> dict[str, object]:
    mus = frange(mu_min, mu_max, mu_step)
    samples = [analyze_tc(alpha2f_path, mu) for mu in mus]
    tc_values = [float(sample["tc_K"]) for sample in samples]
    tc_min = min(tc_values)
    tc_max = max(tc_values)
    tc_spread = tc_max - tc_min
    if tc_min >= 5.0:
        robustness = "robust-high"
    elif tc_min >= 1.0:
        robustness = "robust-low"
    elif tc_max >= 1.0:
        robustness = "sensitive"
    else:
        robustness = "fragile"
    return {
        "path": str(alpha2f_path),
        "mu_window": [mu_min, mu_max],
        "mu_step": mu_step,
        "tc_min_K": tc_min,
        "tc_max_K": tc_max,
        "tc_spread_K": tc_spread,
        "robustness_class": robustness,
        "samples": [{"mu_star": sample["mu_star"], "tc_K": sample["tc_K"]} for sample in samples],
        "observations": ["Tc sensitivity was estimated by sweeping the Allen-Dynes formula over a range of mu* values."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze Tc sensitivity over a range of mu* values.")
    parser.add_argument("--alpha2f-path", required=True)
    parser.add_argument("--mu-min", type=float, default=0.08)
    parser.add_argument("--mu-max", type=float, default=0.15)
    parser.add_argument("--mu-step", type=float, default=0.01)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = analyze(Path(args.alpha2f_path).expanduser().resolve(), args.mu_min, args.mu_max, args.mu_step)
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
