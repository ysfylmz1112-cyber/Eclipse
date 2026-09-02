import json
from pathlib import Path


class SaveSystem:
    """JSON save/load helper for Eclipse runtime state."""

    def __init__(self, filename="eclipse_save.json"):
        self.path = Path(filename)

    def save(self, state, mission):
        payload = {
            "version": 1,
            "state": state.to_dict(),
            "mission": mission.to_dict(),
        }
        self.path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def load(self, state, mission):
        if not self.path.exists():
            return False
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            state.from_dict(payload.get("state", {}))
            mission.from_dict(payload.get("mission", {}))
            return True
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            return False
