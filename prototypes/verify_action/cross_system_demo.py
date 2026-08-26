from __future__ import annotations

import argparse
import json

from cross_system_proof import run_all_scenarios, run_named_scenario


def _text_result(result) -> str:
    lines = [
        f"SCENARIO: {result.scenario}",
        f"VERDICT: {result.verdict}",
        (
            "EVIDENCE: "
            f"provider={result.provider_status}, "
            f"rail_effects={result.rail_effects}, "
            f"ledger_effects={result.ledger_effects}"
        ),
        (
            "RETRY CONTROL: "
            f"attempts={result.attempts}, owner={result.reservation_winners}, "
            f"rejected={result.rejected_attempts}"
        ),
        f"RECEIPT: {'VERIFIED' if result.receipt_verified else 'INVALID'} {result.receipt_digest}",
    ]
    lines.extend(f"NOTE: {note}" for note in result.notes)
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Demonstrate cross-system payment evidence and retry safety."
    )
    parser.add_argument(
        "--scenario",
        choices=(
            "all",
            "verified",
            "safe-to-retry",
            "unverified",
            "reconcile-required",
            "concurrent-retry",
        ),
        default="concurrent-retry",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument(
        "--include-receipt",
        action="store_true",
        help="Include full receipt bundles in JSON output.",
    )
    args = parser.parse_args()

    results = (
        run_all_scenarios()
        if args.scenario == "all"
        else [run_named_scenario(args.scenario)]
    )
    if args.format == "json":
        print(
            json.dumps(
                [
                    result.to_dict(include_receipt=args.include_receipt)
                    for result in results
                ],
                indent=2,
                sort_keys=True,
            )
        )
        return

    print("THE PROOF BREAKS BETWEEN SYSTEMS")
    print("Provider state is not the same thing as economic finality.\n")
    print("\n\n".join(_text_result(result) for result in results))


if __name__ == "__main__":
    main()
