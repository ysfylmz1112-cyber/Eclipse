class GameState:
    """Central runtime state for Eclipse.

    This module is intentionally independent from Panda3D so gameplay systems can
    be tested without starting the renderer.
    """

    def __init__(self):
        self.health = 100.0
        self.stamina = 100.0
        self.paused = False
        self.flashlight = True
        self.found_terminals = set()

    def clamp(self):
        self.health = max(0.0, min(100.0, float(self.health)))
        self.stamina = max(0.0, min(100.0, float(self.stamina)))

    def to_dict(self):
        return {
            "health": self.health,
            "stamina": self.stamina,
            "paused": self.paused,
            "flashlight": self.flashlight,
            "found_terminals": sorted(self.found_terminals),
        }

    def from_dict(self, data):
        self.health = float(data.get("health", 100.0))
        self.stamina = float(data.get("stamina", 100.0))
        self.paused = bool(data.get("paused", False))
        self.flashlight = bool(data.get("flashlight", True))
        self.found_terminals = set(data.get("found_terminals", []))
        self.clamp()
