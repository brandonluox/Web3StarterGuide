from __future__ import annotations

import argparse
import json
import random
import secrets
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Iterable, List

from planner import PlanBook


@dataclass
class AuroraLedger:
    """A small helper to shape payloads and record design notes."""

    network: str = "testnet"
    rpc_endpoint: str = "https://rpc.testnet.zetainfra.example"
    record_dir: Path = Path("records")
    preferred_ops: List[str] = field(default_factory=lambda: ["mint", "swap", "stake"])

    def ensure_record_dir(self) -> Path:
        """Ensure the records folder exists and return its path."""
        self.record_dir.mkdir(exist_ok=True)
        return self.record_dir

    def describe(self) -> str:
        """Return a short description of the current configuration."""
        return (
            f"AuroraLedger on {self.network} using {self.rpc_endpoint} "
            f"tracking ops {', '.join(self.preferred_ops)}."
        )

    def create_payload(
        self,
        op_type: str,
        target: str,
        amount: float,
        note: str = "",
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """Build a reproducible payload for a small Web3 action."""
        metadata = metadata or {}
        payload = {
            "id": secrets.token_hex(10),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "network": self.network,
            "op_type": op_type,
            "target": target,
            "amount": amount,
            "note": note,
            "metadata": metadata,
            "simulation": {
                "rpc": self.rpc_endpoint,
                "priority": random.choice(["low", "medium", "high"]),
            },
        }
        return payload

    def dump_record(self, payload: Dict[str, Any], plan: str | None = None) -> Path:
        """Persist payload details to the record folder."""
        record_path = self.ensure_record_dir() / f"{payload['id']}.json"
        payload_record = {
            "payload": payload,
            "plan": plan,
            "capture_time": datetime.utcnow().isoformat() + "Z",
        }
        record_path.write_text(json.dumps(payload_record, indent=2))
        return record_path

    def plan_suggestion(self, hints: Iterable[str]) -> str:
        """Return a quick suggestion of what to tackle next."""
        options = list(hints)
        if not options:
            return "No next steps queued; jot down a todo."
        return random.choice(options)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AuroraLedger ships a small planner and payload recorder."
    )
    parser.add_argument("--describe", action="store_true", help="Describe the current build.")
    parser.add_argument("--plan", help="Capture a short plan bullet.")
    parser.add_argument("--urgency", choices=["low", "medium", "high"], default="low", help="Triage level for the plan.")
    parser.add_argument("--tags", nargs="+", help="Tags to attach to the plan entry.")
    parser.add_argument("--op", choices=["mint", "swap", "stake"], help="Operation type.")
    parser.add_argument("--target", help="Target account or contract.")
    parser.add_argument("--amount", type=float, default=0.0)
    parser.add_argument("--note", default="", help="Optional narrative.")
    parser.add_argument("--hints", nargs="+", help="Possible next steps during this sprint.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ledger = AuroraLedger()
    plans = PlanBook()

    if args.describe:
        print(ledger.describe())
    if args.plan:
        entry_path = plans.add_entry(args.plan, urgency=args.urgency, tags=args.tags)
        print("Plan logged:", entry_path)
        print("Plan saved:", ledger.plan_suggestion([args.plan]))
    if args.hints:
        print("Hint suggestion:", ledger.plan_suggestion(args.hints))
    if args.op and args.target:
        payload = ledger.create_payload(
            op_type=args.op,
            target=args.target,
            amount=args.amount,
            note=args.note,
        )
        record_path = ledger.dump_record(payload, plan=args.plan)
        print("Payload recorded at", record_path)


if __name__ == "__main__":
    main()
