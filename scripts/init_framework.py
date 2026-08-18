#!/usr/bin/env python3
"""Create a non-overwriting working draft for a measurement framework run."""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

GATE_NAMES = (
    "journey_completeness",
    "journey_appropriateness",
    "objective_completeness",
    "objective_appropriateness",
    "kpi_completeness",
    "kpi_appropriateness",
    "requirement_traceability",
    "overall",
)


def build_draft(
    *,
    title: str,
    scope: str,
    language: str,
    target_state: str,
    scope_claim: str,
    target_sites: list[str],
    products: list[str],
    markets: list[str],
    audiences: list[str],
    source_reference: str,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    source_state = {"as_is": "as_is", "to_be": "to_be", "hybrid": "both"}[target_state]
    gates = {
        name: {
            "status": "fail",
            "tested_at": now,
            "rationale": "Not yet evaluated; complete the relevant analysis and closure tests.",
            "exception_ids": [],
        }
        for name in GATE_NAMES
    }
    return {
        "schema_version": "1.2.0",
        "document": {
            "title": title,
            "version": "0.1-draft",
            "date": date.today().isoformat(),
            "language": language,
            "run_id": f"run_{uuid.uuid4().hex}",
            "target_state": target_state,
            "scope_claim": scope_claim,
            "scope": scope,
            "target_sites": target_sites,
            "products": products,
            "markets": markets,
            "audiences": audiences,
        },
        "sources": [
            {
                "source_id": "source_intake",
                "source_type": "user_input",
                "reference": source_reference,
                "evidence_role": "business_requirement",
                "state": source_state,
                "supports": ["Initial scope and task description"],
            }
        ],
        "discovery_candidates": [],
        "journeys": [],
        "objective_considerations": [],
        "objectives": [],
        "kpi_considerations": [],
        "kpis": [],
        "dimensions": [],
        "measurement_requirements": [],
        "alignment": [],
        "unlinked_measurements": [],
        "assumptions": [],
        "exceptions": [],
        "quality_gates": gates,
    }


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--language", default="en")
    parser.add_argument(
        "--target-state", choices=("as_is", "to_be", "hybrid"), default="as_is"
    )
    parser.add_argument(
        "--scope-claim", choices=("whole_site", "journey_subset"), default="whole_site"
    )
    parser.add_argument("--site", action="append", default=[], dest="target_sites")
    parser.add_argument("--product", action="append", default=[], dest="products")
    parser.add_argument("--market", action="append", default=[], dest="markets")
    parser.add_argument("--audience", action="append", default=[], dest="audiences")
    parser.add_argument("--source-reference", default="User request")
    parser.add_argument("--output", "-o", required=True, type=Path)
    parser.add_argument(
        "--force", action="store_true", help="Replace an existing draft intentionally"
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    if args.output.exists() and not args.force:
        print(
            f"ERROR: output already exists: {args.output}; use --force only for an intentional replacement",
            file=sys.stderr,
        )
        return 1

    draft = build_draft(
        title=args.title,
        scope=args.scope,
        language=args.language,
        target_state=args.target_state,
        scope_claim=args.scope_claim,
        target_sites=args.target_sites,
        products=args.products,
        markets=args.markets,
        audiences=args.audiences,
        source_reference=args.source_reference,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(draft, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"WROTE DRAFT: {args.output}")
    print(
        "NEXT: replace empty inventories, resolve every gate, then run validate_framework.py --delivery"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
