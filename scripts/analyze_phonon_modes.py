#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path


def analyze(path: Path, soft_threshold: float = 1.0) -> dict[str, object]:
    freqs = [float(line.split()[0]) for line in path.read_text().splitlines() if line.split()]
    if not freqs:
        raise SystemExit("Phonon-mode file contains no frequencies")
    imaginary = [freq for freq in freqs if freq < 0]
    soft = [freq for freq in freqs if 0 <= freq < soft_threshold]
    return {
        "path": str(path),
        "min_frequency": min(freqs),
        "imaginary_mode_count": len(imaginary),
        "soft_mode_count": len(soft),
        "observations": ["Phonon-mode stability summary extracted from the sampled frequencies."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze a set of phonon frequencies.")
    parser.add_argument("path")
    parser.add_argument("--soft-threshold", type=float, default=1.0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = analyze(Path(args.path).expanduser().resolve(), args.soft_threshold)
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
