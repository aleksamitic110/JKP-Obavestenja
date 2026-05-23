from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class JsonStateStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"processed_urls": []}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def get_processed_urls(self) -> set[str]:
        state = self.load()
        return set(state.get("processed_urls", []))

    def mark_processed(self, urls: set[str]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        state = self.load()
        processed = set(state.get("processed_urls", []))
        processed.update(urls)
        state["processed_urls"] = sorted(processed)
        self.path.write_text(
            json.dumps(state, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

