from __future__ import annotations

import argparse
import json
import random
import secrets
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Iterable, List

from network_catalog import NetworkCatalog
from planner import PlanBook
from payload_validator import validate_payload


@dataclass
class AuroraLedger:
    """A small helper to shape payloads and record design notes."""

    network: str = "testnet"
    rpc_endpoint: str = "https://rpc.testnet.zetainfra.example"
    record_dir: Path = Path("records")
    preferred_ops: List[str] = field(default_factory=lambda: ["mint", "swap", "stake"])
    catalog: NetworkCatalog | None = None

    def ensure_record_dir(self) -> Path:
        """Ensure the records folder exists and return its path."""
        self.record_dir.mkdir(exist_ok=True)
        return self.record_dir

    def list_records(self) -> List[Path]:
        """Return the saved record files, sorted by name."""
        self.ensure_record_dir()
        return sorted(self.record_dir.glob("*.json"))

    def summarize_records(self) -> Dict[str, Any]:
        """Return a quick count and total of the recorded payloads."""
        records = self.list_records()
        op_counts: Dict[str, int] = {}
        total_amount = 0.0
        for record in records:
            try:
                data = json.loads(record.read_text())
                payload = data.get("payload", {})
                op = payload.get("op_type", "unknown")
                amount = float(payload.get("amount", 0))
                op_counts[op] = op_counts.get(op, 0) + 1
                total_amount += amount
            except (ValueError, FileNotFoundError):
                continue
        return {
            "count": len(records),
            "total_amount": total_amount,
            "ops": op_counts,
        }

    def describe(self) -> str:
        """Return a short description of the current configuration."""
        return (
            f"AuroraLedger on {self.network} using {self.rpc_endpoint} "
            f"tracking ops {', '.join(self.preferred_ops)}."
        )

    def __post_init__(self) -> None:
        if self.catalog:
            entry = self.catalog.profile(self.network)
            if entry:
                self.rpc_endpoint = entry.rpc
                self.network = entry.name

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
        validate_payload(payload)
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
    parser.add_argument("--list-records", action="store_true", help="List recorded payloads.")
    parser.add_argument("--network", default="testnet", help="Select the named RPC profile.")
    parser.add_argument("--list-networks", action="store_true", help="List configured RPC profiles.")
    parser.add_argument("--summary", action="store_true", help="Show payload summary.")
    parser.add_argument("--op", choices=["mint", "swap", "stake"], help="Operation type.")
    parser.add_argument("--target", help="Target account or contract.")
    parser.add_argument("--amount", type=float, default=0.0)
    parser.add_argument("--note", default="", help="Optional narrative.")
    parser.add_argument("--hints", nargs="+", help="Possible next steps during this sprint.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    catalog = NetworkCatalog()
    ledger = AuroraLedger(network=args.network, catalog=catalog)
    plans = PlanBook()

    if args.list_networks:
        profiles = catalog.list_profiles()
        if not profiles:
            print("No network profiles found.")
        else:
            print("Available profiles:")
            for profile in profiles:
                print(f"- {profile.name}: {profile.description} ({profile.rpc})")

    if args.describe:
        print(ledger.describe())
    if args.plan:
        entry_path = plans.add_entry(args.plan, urgency=args.urgency, tags=args.tags)
        print("Plan logged:", entry_path)
        print("Plan saved:", ledger.plan_suggestion([args.plan]))
    if args.list_records:
        saved = ledger.list_records()
        if not saved:
            print("No payloads recorded yet.")
        else:
            print("Saved payloads:")
            for record in saved:
                print("-", record.name)
    if args.summary:
        summary = ledger.summarize_records()
        print(
            f"Payload summary: {summary['count']} entries, {summary['total_amount']} total amount."
        )
        for op, count in sorted(summary["ops"].items()):
            print(f"  {op}: {count}")
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
