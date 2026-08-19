#!/usr/bin/env python3
"""Report candidate, target-evidence, and material-state coverage without mutation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from diagnostics import candidate_census


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("framework", type=Path)
    parser.add_argument(
        "--json", action="store_true", dest="json_output", help="Emit JSON"
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    try:
        data = json.loads(args.framework.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    census = candidate_census(data)
    if args.json_output:
        print(json.dumps(census, indent=2, ensure_ascii=False))
        return 0

    print(f"Candidates: {census['candidate_total']}")
    print(f"Material candidates: {census['material_candidate_total']}")
    for candidate_type, counts in census["by_type"].items():
        summary = ", ".join(f"{key}={value}" for key, value in counts.items())
        print(f"- {candidate_type}: {summary}")
    for label, key in (
        ("Material unresolved", "unresolved_material_candidate_ids"),
        ("Journeys without candidates", "journeys_without_discovery_candidates"),
    ):
        values = census[key]
        print(f"{label}: {', '.join(values) if values else 'none'}")
    if census["intake_baseline_present"]:
        values = census["included_targets_without_representative_sources"]
        print(
            "Included targets without representative sources: "
            f"{', '.join(values) if values else 'none'}"
        )
    else:
        print("Intake baseline: not available in legacy schema")
    state_summary = ", ".join(
        f"{key}={value}" for key, value in census["state_decision_resolutions"].items()
    )
    print(f"State decisions: {state_summary or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
