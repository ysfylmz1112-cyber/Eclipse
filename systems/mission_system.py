class MissionSystem:
    """Small, data-driven mission tracker for Eclipse."""

    def __init__(self, required_terminals=3):
        self.required_terminals = int(required_terminals)
        self.found = set()

    @property
    def progress(self):
        return min(len(self.found), self.required_terminals)

    @property
    def completed(self):
        return self.progress >= self.required_terminals

    def discover_terminal(self, terminal_id):
        terminal_id = str(terminal_id)
        if self.completed:
            return False
        before = len(self.found)
        self.found.add(terminal_id)
        return len(self.found) != before

    def objective_text(self):
        if self.completed:
            return "GÖREV TAMAMLANDI: BÖLGE KEŞFEDİLDİ"
        return f"GÖREV: {self.progress}/{self.required_terminals} terminal bulundu"

    def to_dict(self):
        return {
            "required_terminals": self.required_terminals,
            "found": sorted(self.found),
        }

    def from_dict(self, data):
        self.required_terminals = int(data.get("required_terminals", self.required_terminals))
        self.found = set(str(x) for x in data.get("found", []))
