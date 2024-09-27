# room.py
class Room:
    def __init__(self, room_type, size, contents, num_exits):
        self.room_type = room_type
        self.size = size
        self.contents = contents
        self.num_exits = num_exits
        self.exits = []
        self.connections = []
        self.monster = None
        self.treasure = None
        self.trap = None
        self.special = None

    def add_exit(self, location, direction):
        self.exits.append((location, direction))

    def connect_to(self, other_room):
        self.connections.append(other_room)
        other_room.connections.append(self)

    def __str__(self):
        room_str = f"Room: {self.room_type}, Size: {self.size}, Contents: {self.contents}, Exits: {len(self.exits)}"
        if self.monster:
            room_str += f"\n  Monster: {self.monster}"
        if self.treasure:
            room_str += f"\n  Treasure: {self.treasure}"
        if self.trap:
            room_str += f"\n  Trap: {self.trap}"
        if self.special:
            room_str += f"\n  Special: {self.special}"
        return room_str
