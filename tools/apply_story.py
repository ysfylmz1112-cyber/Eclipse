from pathlib import Path

path = Path('main.py')
text = path.read_text(encoding='utf-8')

if 'from systems.eclipse_story import EclipseStory' not in text:
    text = text.replace(
        'from systems.graphics_system import GraphicsSystem\n',
        'from systems.graphics_system import GraphicsSystem\nfrom systems.eclipse_story import EclipseStory\n',
        1,
    )

if 'self.story = EclipseStory(self)' not in text:
    text = text.replace(
        '        self.graphics_system = GraphicsSystem(self)\n',
        '        self.graphics_system = GraphicsSystem(self)\n        self.story = EclipseStory(self)\n',
        1,
    )

if 'self.story.update(dt)' not in text:
    text = text.replace(
        '        self.graphics_system.update(dt)\n',
        '        self.graphics_system.update(dt)\n        self.story.update(dt)\n',
        1,
    )

path.write_text(text, encoding='utf-8')
print('Eclipse story system applied to main.py')
