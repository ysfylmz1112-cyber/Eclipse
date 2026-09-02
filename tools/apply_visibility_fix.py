from pathlib import Path

path = Path('main.py')
text = path.read_text(encoding='utf-8')
old = "        self.character.show()\n        self.character.flattenLight()\n"
new = "        self.character.show()\n        # Keep the player visible under the scene lighting.\n        self.character.clearLight()\n        self.character.setLightOff()\n"
if old not in text:
    raise SystemExit('Beklenen karakter aydınlatma bölümü bulunamadı.')
path.write_text(text.replace(old, new, 1), encoding='utf-8')
print('Eclipse karakter görünürlük düzeltmesi uygulandı.')
