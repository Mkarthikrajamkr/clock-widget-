"""Local JSON persistence for trading blocks."""

from __future__ import annotations

import json
import os
from pathlib import Path

from .models import TradingBlock


class SessionStorage:
    """Read and write sessions to a user-specific JSON file."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or self.default_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def default_path() -> Path:
        """Return a Windows-friendly app data path with a cross-platform fallback."""

        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / "TradingTimeBlockManager" / "sessions.json"
        return Path.home() / ".trading_time_block_manager" / "sessions.json"

    def load(self) -> list[TradingBlock]:
        """Load all saved sessions. Invalid files return an empty list."""

        if not self.path.exists():
            return []
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
        return [TradingBlock.from_dict(item) for item in payload.get("sessions", [])]

    def save(self, blocks: list[TradingBlock]) -> None:
        """Persist sessions with pretty JSON for easy manual editing/export."""

        payload = {"sessions": [block.to_dict() for block in blocks]}
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def export_to(self, destination: Path, blocks: list[TradingBlock]) -> None:
        """Write a portable session-template JSON file."""

        payload = {"sessions": [block.to_dict() for block in blocks]}
        destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def import_from(self, source: Path) -> list[TradingBlock]:
        """Read sessions from an exported template."""

        payload = json.loads(source.read_text(encoding="utf-8"))
        return [TradingBlock.from_dict(item) for item in payload.get("sessions", [])]
