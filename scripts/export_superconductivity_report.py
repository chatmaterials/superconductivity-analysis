#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from analyze_alpha2f import analyze as analyze_alpha2f
from analyze_phonon_modes import analyze as analyze_phonons
from estimate_tc import analyze as analyze_tc


def render_markdown(epc: dict[str, object], phonons: dict[str, object] | None, tc: dict[str, object]) -> str:
    lines = [
        "# Superconductivity Analysis Report",
        "",
        "## Electron-Phonon Coupling",
        f"- Lambda: `{epc['lambda_ep']:.4f}`",
        f"- Omega_log (meV): `{epc['omega_log_meV']:.4f}`",
        f"- Omega_log (K): `{epc['omega_log_K']:.4f}`",
        "",
        "## Tc Estimate",
        f"- mu*: `{tc['mu_star']:.3f}`",
        f"- Tc (K): `{tc['tc_K']:.4f}`",
    ]
    if phonons is not None:
        lines.extend(
            [
                "",
                "## Phonon Stability",
                f"- Minimum frequency: `{phonons['min_frequency']:.4f}`",
                f"- Imaginary mode count: `{phonons['imaginary_mode_count']}`",
                f"- Soft mode count: `{phonons['soft_mode_count']}`",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a markdown superconductivity-analysis report.")
    parser.add_argument("--alpha2f-path", required=True)
    parser.add_argument("--phonon-path")
    parser.add_argument("--mu-star", type=float, default=0.10)
    parser.add_argument("--output")
    args = parser.parse_args()
    alpha2f = Path(args.alpha2f_path).expanduser().resolve()
    epc = analyze_alpha2f(alpha2f)
    phonons = analyze_phonons(Path(args.phonon_path).expanduser().resolve()) if args.phonon_path else None
    tc = analyze_tc(alpha2f, args.mu_star)
    output = Path(args.output).expanduser().resolve() if args.output else Path.cwd() / "SUPERCONDUCTIVITY_REPORT.md"
    output.write_text(render_markdown(epc, phonons, tc))
    print(output)


if __name__ == "__main__":
    main()
