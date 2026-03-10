#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


MEV_TO_K = 11.60451812


def load_rows(path: Path) -> list[tuple[float, float]]:
    rows = []
    for line in path.read_text().splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        omega = float(parts[0])
        a2f = float(parts[1])
        if omega <= 0:
            continue
        rows.append((omega, a2f))
    if len(rows) < 2:
        raise SystemExit("alpha2F file must contain at least two positive-frequency rows")
    return rows


def trapz_integral(rows: list[tuple[float, float]], fn) -> float:
    total = 0.0
    for (x0, y0), (x1, y1) in zip(rows, rows[1:]):
        total += 0.5 * (fn(x0, y0) + fn(x1, y1)) * (x1 - x0)
    return total


def analyze(path: Path) -> dict[str, object]:
    rows = load_rows(path)
    lambda_ep = 2.0 * trapz_integral(rows, lambda w, a: a / w)
    if lambda_ep <= 0:
        raise SystemExit("Computed lambda is non-positive")
    log_integral = 2.0 * trapz_integral(rows, lambda w, a: (a / w) * math.log(w))
    omega_log_meV = math.exp(log_integral / lambda_ep)
    return {
        "path": str(path),
        "lambda_ep": lambda_ep,
        "omega_log_meV": omega_log_meV,
        "omega_log_K": omega_log_meV * MEV_TO_K,
        "observations": ["Electron-phonon coupling summary extracted from the alpha^2F spectrum."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze an alpha^2F spectrum.")
    parser.add_argument("path")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = analyze(Path(args.path).expanduser().resolve())
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
