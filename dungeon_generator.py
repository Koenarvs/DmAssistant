import json
import random
from room import Room
from level import Level
from dungeon import Dungeon
from utils import roll_dice

class DungeonGenerator:
    def __init__(self):
        self.dungeon = Dungeon()
        self.load_data()

    def load_data(self):
        # Load data from dungeon_data.json which has tables for random generation
        with open('dungeon_data.json', 'r') as f:
            self.data = json.load(f)

    def roll_table(self, table_name):
        """
        Roll on the specified table and return the result.
        """
        table = self.data[table_name]
        roll = random.randint(1, 100)  # Adjust based on the table's range
        for entry in table:
            if roll <= entry["chance"]:
                return entry["result"]
        return None

    def generate_dungeon(self, num_levels):
        """
        Generate multiple levels for the dungeon
        """
        for _ in range(num_levels):
            level = self.generate_level()
            self.dungeon.add_level(level)

    def generate_level(self):
        """
        Generate a single level with rooms, exits, and features.
        """
        level = Level()
        start_area = self.choose_start_area()
        level.add_room(start_area)

        while len(level.rooms) < 20:  # Adjust number of rooms per level
            new_room = self.generate_room()
            level.add_room(new_room)

        self.connect_rooms(level)
        return level

    def choose_start_area(self):
        """
        Choose a random start area using dungeon generation rules from the provided tables.
        """
        # Roll for size, contents, and number of exits using tables from your data
        size = self.roll_table("CHAMBERS_AND_ROOMS_SHAPE_AND_SIZE")
        contents = self.roll_table("CHAMBER_OR_ROOM_CONTENTS")
        num_exits = self.roll_table("NUMBER_OF_EXITS")
        
        # Create and return the room with the correct parameters
        return Room(room_type="Start Area", size=size, contents=contents, num_exits=num_exits)

    def generate_room(self):
        """
        Generate a random room with exits and contents, following the tables provided.
        """
        # Roll for room type, size, contents, and number of exits
        room_type = self.roll_table("CHAMBERS_AND_ROOMS_SHAPE_AND_SIZE")
        size = self.determine_room_size()  # Or roll using roll_table if this comes from a table
        contents = self.roll_table("CHAMBER_OR_ROOM_CONTENTS")
        num_exits = self.determine_num_exits()  # Roll using the NUMBER_OF_EXITS table

        # Create a new Room instance
        room = Room(
            room_type=room_type,
            size=size,
            contents=contents,
            num_exits=num_exits
        )

        # Generate exits for the room
        for _ in range(room.num_exits):
            exit_location = self.roll_table("EXIT_LOCATION")
            exit_direction = self.roll_table("EXIT_DIRECTION")
            room.add_exit(exit_location, exit_direction)  # Assuming add_exit is a method of Room class

        # Add additional contents based on room type
        if room.contents == "Monster only" or room.contents == "Monster and treasure":
            room.monster = self.generate_monster()  # Assuming generate_monster method exists
        if room.contents == "Monster and treasure" or room.contents == "Treasure":
            room.treasure = self.generate_treasure()  # Assuming generate_treasure method exists
        if room.contents == "Trick/Trap":
            room.trap = self.generate_trap()  # Assuming generate_trap method exists
        if room.contents == "Special":
            room.special = self.generate_special()  # Assuming generate_special method exists

        return room

    def determine_room_size(self):
        """
        Determine room size using the 'UNUSUAL_SIZE' table.
        """
        return self.roll_table("UNUSUAL_SIZE")

    def determine_num_exits(self):
        """
        Determine number of exits for the room using 'NUMBER_OF_EXITS'.
        """
        num_exits = self.roll_table("NUMBER_OF_EXITS")
        
        if 'd' in num_exits:
            return roll_dice(num_exits)
        
        return int(num_exits)

    def connect_rooms(self, level):
        """
        Connect rooms with passages/corridors. Logic can be improved for realistic connectivity.
        """
        for i, room in enumerate(level.rooms[:-1]):
            next_room = level.rooms[i + 1]
            room.connect_to(next_room)

    def generate_monster(self):
        """
        Generate a random monster from the 'MONSTER_ENCOUNTERS' table.
        """
        return self.roll_table("MONSTER_ENCOUNTERS")

    def generate_treasure(self):
        """
        Generate treasure from 'TREASURE_TYPE', 'TREASURE_CONTAINER', and 'TREASURE_GUARD'.
        """
        treasure_type = self.roll_table("TREASURE_TYPE")
        treasure_container = self.roll_table("TREASURE_CONTAINER")
        treasure_guard = self.roll_table("TREASURE_GUARD")
        return f"{treasure_type} in {treasure_container}, guarded by {treasure_guard}"

    def generate_trap(self):
        """
        Generate a trap from 'TRAPS'.
        """
        return self.roll_table("TRAPS")

    def generate_special(self):
        """
        Generate a special feature from 'SPECIAL_FEATURES'.
        """
        return self.roll_table("SPECIAL_FEATURES")
