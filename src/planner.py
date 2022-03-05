from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List


@dataclass
class PlanEntry:
    """Simple record to track what needs attention next."""

    id: str
    note: str
    urgency: str
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class PlanBook:
    """Keeps an append-only journal of my next steps."""

    def __init__(self, plans_dir: Path | str = "plans") -> None:
        self.plans_dir = Path(plans_dir)
        self.plans_dir.mkdir(exist_ok=True)

    def _sample_id(self) -> str:
        return f"plan-{random.randint(10_000, 99_999)}"

    def add_entry(self, note: str, urgency: str = "low", tags: List[str] | None = None) -> Path:
        metadata: Dict[str, str] = {"urgency": urgency, "tags": ", ".join(tags or [])}
        entry = PlanEntry(id=self._sample_id(), note=note, urgency=urgency, tags=tags or [])
        payload = {
            "entry": entry.__dict__,
            "metadata": metadata,
            "logged_at": datetime.utcnow().isoformat() + "Z",
        }
        store_path = self.plans_dir / f"{entry.id}.json"
        store_path.write_text(json.dumps(payload, indent=2))
        return store_path
