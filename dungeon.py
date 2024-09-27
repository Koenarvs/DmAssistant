# dungeon.py
from level import Level

class Dungeon:
    def __init__(self):
        self.levels = []

    def add_level(self, level: Level):
        self.levels.append(level)

    def __str__(self):
        dungeon_str = f"Dungeon with {len(self.levels)} levels.\n"
        for i, level in enumerate(self.levels, start=1):
            dungeon_str += f"  Level {i}: {len(level.rooms)} rooms.\n"
        return dungeon_str
