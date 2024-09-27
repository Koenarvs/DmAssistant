# level.py
from room import Room

class Level:
    def __init__(self):
        self.rooms = []

    def add_room(self, room: Room):
        self.rooms.append(room)

    def __str__(self):
        return f"Level with {len(self.rooms)} rooms."
