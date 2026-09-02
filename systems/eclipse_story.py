"""Eclipse opening story/event controller.

The first playable milestone is the solar-eclipse opening. The system is
kept separate from main.py so the story can grow without making the game
loop difficult to maintain.
"""
from direct.gui.DirectGui import DirectLabel
from panda3d.core import TextNode


class EclipseStory:
    def __init__(self, game):
        self.game = game
        self.elapsed = 0.0
        self.phase = "eclipse"
        self.phase_time = 0.0
        self.triggered = False
        self.label = DirectLabel(
            text="",
            scale=.050,
            pos=(0, 0, .72),
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
        )
        self.label.reparentTo(game.a2dTopCenter)
        self._set("GÜNEŞ TUTULMASI\nGÖZLEM BAŞLADI")

    def _set(self, text):
        self.label.setText(text)

    def update(self, dt):
        if self.triggered or getattr(self.game, "paused", False):
            return
        self.elapsed += dt
        self.phase_time += dt

        # Prototype timing: a short playable eclipse, followed by the
        # dramatic light-travel delay. The real Sun-Earth delay is ~8m20s;
        # the prototype uses compressed time for gameplay testing.
        if self.phase == "eclipse" and self.phase_time >= 18.0:
            self.phase = "waiting"
            self.phase_time = 0.0
            self._set("TUTULMA SONA ERDİ\nGÖKYÜZÜ SESSİZ...")
        elif self.phase == "waiting" and self.phase_time >= 12.0:
            self.phase = "anomaly"
            self.phase_time = 0.0
            self._set("GÜNEŞ'TE ANOMALİ TESPİT EDİLDİ\nVERİLER DÜNYA'YA ULAŞIYOR...")
        elif self.phase == "anomaly" and self.phase_time >= 8.0:
            self.phase = "active"
            self.triggered = True
            self._set("ECLIPSE\nANOMALİ BAŞLADI")
            self.game.message("GÜNEŞ ANOMALİSİ: İLK VERİ ALINDI")
