from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
main_path = ROOT / 'main.py'
text = main_path.read_text(encoding='utf-8')

if 'from player_character import EclipseCharacter' not in text:
    text = text.replace('from systems.graphics_system import GraphicsSystem\n', 'from systems.graphics_system import GraphicsSystem\nfrom player_character import EclipseCharacter\n')

start = text.index('    def player(self):')
end = text.index('    def lights(self):', start)

new_player = '''    def player(self):\n        self.p = self.render.attachNewNode('Player')\n        self.p.setPos(0, -2, 0.70)\n        self.character = self.p.attachNewNode('EclipseCharacter')\n        self.character.setPos(0, 0, 0)\n        self.character.setScale(1.0)\n        self.character_model = EclipseCharacter(self, self.character)\n        self.character.show()\n\n'''

text = text[:start] + new_player + text[end:]
main_path.write_text(text, encoding='utf-8')
print('Eclipse karakter sistemi kuruldu: main.py güncellendi.')
