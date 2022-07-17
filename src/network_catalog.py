from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


@dataclass
class NetworkProfile:
    """Represents a single RPC profile for AuroraLedger."""

    name: str
    rpc: str
    explorer: str
    description: str = ""


class NetworkCatalog:
    """Loads RPC profiles from a JSON snapshot."""

    def __init__(self, source: Path | str = "data/networks.json") -> None:
        self.source = Path(source)
        self.profiles: Dict[str, NetworkProfile] = self._load_profiles()

    def _load_profiles(self) -> Dict[str, NetworkProfile]:
        if not self.source.exists():
            return {}
        raw = json.loads(self.source.read_text())
        profile_map = {}
        for name, definition in raw.get("rpc_profiles", {}).items():
            profile_map[name] = NetworkProfile(
                name=name,
                rpc=definition.get("rpc", ""),
                explorer=definition.get("explorer", ""),
                description=definition.get("description", ""),
            )
        return profile_map

    def profile(self, name: str) -> NetworkProfile | None:
        """Return the named profile if it exists."""
        return self.profiles.get(name)

    def list_profiles(self) -> List[NetworkProfile]:
        """Return the loaded profiles in alphabetical order."""
        return sorted(self.profiles.values(), key=lambda entry: entry.name)
