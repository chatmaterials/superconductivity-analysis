#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from analyze_alpha2f import analyze as analyze_alpha2f
from analyze_phonon_modes import analyze as analyze_phonons
from analyze_tc_sensitivity import analyze as analyze_tc_sensitivity
from estimate_tc import analyze as analyze_tc


def screening_note(epc: dict[str, object], phonons: dict[str, object] | None, tc: dict[str, object]) -> str:
    if phonons is not None and phonons["imaginary_mode_count"] > 0:
        return "The coupling may look promising, but imaginary phonon modes indicate a structural instability that undercuts simple superconductivity screening."
    if tc["tc_K"] >= 5.0 and (phonons is None or phonons["stability_class"] != "unstable"):
        return f"This case combines `{epc['coupling_regime']}` electron-phonon coupling with a `{tc['tc_class']}` Allen-Dynes estimate."
    if phonons is not None and phonons["stability_class"] == "softened":
        return "The sampled phonon spectrum is softened rather than fully unstable; this may enhance coupling, but the system still needs careful stability checks."
    return "This case looks weak-to-moderate in compact EPC screening and may need stronger coupling or a higher characteristic frequency to become competitive."


def render_markdown(epc: dict[str, object], phonons: dict[str, object] | None, tc: dict[str, object], sensitivity: dict[str, object]) -> str:
    lines = [
        "# Superconductivity Analysis Report",
        "",
        "## Electron-Phonon Coupling",
        f"- Lambda: `{epc['lambda_ep']:.4f}`",
        f"- Coupling regime: `{epc['coupling_regime']}`",
        f"- Low-frequency lambda fraction: `{epc['low_frequency_lambda_fraction']:.4f}`",
        f"- Omega_log (meV): `{epc['omega_log_meV']:.4f}`",
        f"- Omega_log (K): `{epc['omega_log_K']:.4f}`",
        "",
        "## Tc Estimate",
        f"- mu*: `{tc['mu_star']:.3f}`",
        f"- Tc (K): `{tc['tc_K']:.4f}`",
        f"- Tc class: `{tc['tc_class']}`",
        "",
        "## Tc Robustness",
        f"- Tc min over mu* window (K): `{sensitivity['tc_min_K']:.4f}`",
        f"- Tc max over mu* window (K): `{sensitivity['tc_max_K']:.4f}`",
        f"- Tc spread over mu* window (K): `{sensitivity['tc_spread_K']:.4f}`",
        f"- Robustness class: `{sensitivity['robustness_class']}`",
    ]
    if phonons is not None:
        lines.extend(
            [
                "",
                "## Phonon Stability",
                f"- Minimum frequency: `{phonons['min_frequency']:.4f}`",
                f"- Stability class: `{phonons['stability_class']}`",
                f"- Imaginary mode count: `{phonons['imaginary_mode_count']}`",
                f"- Soft mode count: `{phonons['soft_mode_count']}`",
            ]
        )
    lines.extend(["", "## Screening Note", f"- {screening_note(epc, phonons, tc)}"])
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
    sensitivity = analyze_tc_sensitivity(alpha2f, 0.08, 0.15, 0.01)
    output = Path(args.output).expanduser().resolve() if args.output else Path.cwd() / "SUPERCONDUCTIVITY_REPORT.md"
    output.write_text(render_markdown(epc, phonons, tc, sensitivity))
    print(output)


if __name__ == "__main__":
    main()
