import random
import json

# Constants
GRID_SIZE = 5  # Each grid square represents 5' x 5'
START_COORD = (0, 0)
MAX_LEVEL = 3  # Define how many levels deep the dungeon can go

# Unique ID generator
def generate_id():
    current_id = 1
    while True:
        yield current_id
        current_id += 1

id_gen = generate_id()

# Helper functions for dice rolls
def roll_die(sides=20):
    return random.randint(1, sides)

def roll_multiple_die(count=1, sides=20):
    return [random.randint(1, sides) for _ in range(count)]

# Data Structures
class Room:
    def __init__(self, room_type, shape, size, coordinates, exits, contents, room_id, level):
        self.id = room_id
        self.type = room_type  # 'Chamber' or 'Room'
        self.shape = shape
        self.size = size  # in sq. ft.
        self.coordinates = coordinates  # (x1, y1, x2, y2)
        self.exits = exits  # List of Exit objects
        self.contents = contents  # Contents based on Table V.F
        self.level = level

class Corridor:
    def __init__(self, corridor_type, length, width, direction, start_coords, end_coords, corridor_id, level):
        self.id = corridor_id
        self.type = corridor_type  # 'Passage' or 'Special Passage'
        self.length = length  # in feet
        self.width = width  # in feet
        self.direction = direction  # e.g., 'Straight', 'Left 90 degrees', etc.
        self.start_coords = start_coords  # (x, y)
        self.end_coords = end_coords  # (x, y)
        self.level = level

class Exit:
    def __init__(self, direction, leads_to):
        self.direction = direction  # 'Left', 'Right', 'Ahead', etc.
        self.leads_to = leads_to  # Room or Corridor object

class Dungeon:
    def __init__(self):
        self.rooms = {}
        self.corridors = {}
        self.stairs = []
        self.level = 1
        self.dungeon_file = "dungeon.txt"

    def generate_dungeon(self):
        # Start with the initial room
        initial_room = self.create_room(START_COORD, self.level)
        self.rooms[initial_room.id] = initial_room
        self.process_room(initial_room)
        self.save_dungeon()

    def create_room(self, center_coords, level):
        room_id = next(id_gen)
        # Roll on Table V to determine chamber or room
        table_v_roll = roll_die()
        chamber_or_room = 'Chamber' if table_v_roll in range(1, 15) else 'Room'
        # Determine shape and size
        shape, size = self.roll_table_v(table_v_roll, chamber_or_room)
        # Determine coordinates based on size and center
        coordinates = self.calculate_coordinates(center_coords, size)
        # Determine contents
        contents = self.roll_table_v_f()
        # Initialize exits list
        exits = []
        return Room(chamber_or_room, shape, size, coordinates, exits, contents, room_id, level)

    def calculate_coordinates(self, center, size):
        # Assuming square rooms for simplicity
        half_size = size ** 0.5 / 2  # Assuming size is area in sq. ft.
        x1 = center[0] - half_size
        y1 = center[1] - half_size
        x2 = center[0] + half_size
        y2 = center[1] + half_size
        return (x1, y1, x2, y2)

    def roll_table_v(self, roll, chamber_or_room):
        # Implement Table V logic
        if chamber_or_room == 'Chamber':
            if roll in [1, 2]:
                shape = 'Square'
                size = 20 * 20
            elif roll in [3,4]:
                shape = 'Square'
                size = 20 * 20
            elif roll in [5,6]:
                shape = 'Square'
                size = 30 * 30
            elif roll in [7,8]:
                shape = 'Square'
                size = 40 * 40
            elif roll in [9,10]:
                shape = 'Rectangular'
                size = 10 * 20
            elif roll in [11,12]:
                shape = 'Rectangular'
                size = 20 * 30
            elif roll in [13,14]:
                shape = 'Rectangular'
                size = 30 * 50
            elif roll in [15,16,17]:
                shape = 'Rectangular'
                size = 40 * 60
            elif roll in [18,19,20]:
                shape = 'Unusual'
                size = self.roll_table_v_b()
        else:  # Room
            if roll in [1, 2]:
                shape = 'Square'
                size = 10 * 10
            elif roll in [3,4]:
                shape = 'Square'
                size = 20 * 20
            elif roll in [5,6]:
                shape = 'Square'
                size = 30 * 30
            elif roll in [7,8]:
                shape = 'Square'
                size = 40 * 40
            elif roll in [9,10]:
                shape = 'Rectangular'
                size = 10 * 20
            elif roll in [11,12]:
                shape = 'Rectangular'
                size = 20 * 30
            elif roll in [13,14]:
                shape = 'Rectangular'
                size = 30 * 50
            elif roll in [15,16,17]:
                shape = 'Rectangular'
                size = 40 * 60
            elif roll in [18,19,20]:
                shape = 'Unusual'
                size = self.roll_table_v_b()
        return shape, size

    def roll_table_v_b(self):
        # Implement Table V.B
        roll = roll_die()
        if roll in [1,2,3]:
            size = 500
        elif roll in [4,5,6]:
            size = 900
        elif roll in [7,8]:
            size = 1200
        elif roll in [9,10]:
            size = 2000
        elif roll in [11,12]:
            size = 2700
        elif roll in [13,14]:
            size = 3400
        elif roll >=15 and roll <=20:
            # Roll again and add to 9-10 (2000)
            additional = self.roll_table_v_b()
            size = 2000 + additional
        return size

    def roll_table_v_f(self):
        # Implement Table V.F
        roll = roll_die()
        if 1 <= roll <= 12:
            contents = 'Empty'
        elif 13 <= roll <= 14:
            contents = 'Monster only'
        elif 15 <= roll <= 17:
            contents = 'Monster and treasure'
        elif roll == 18:
            contents = 'Special stairway'
        elif roll == 19:
            contents = 'Trick/Trap'
        elif roll == 20:
            contents = 'Treasure'
        return contents

    def process_room(self, room):
        # Determine exits based on Table I
        self.check_periodic(room)

    def check_periodic(self, room):
        while True:
            roll = roll_die()
            if 1 <= roll <=2:
                # Continue straight, check again in 60'
                self.handle_continue_straight(room, distance=60)
            elif 3 <= roll <=5:
                # Door
                self.handle_door(room)
            elif 6 <= roll <=10:
                # Side Passage, check again in 30'
                self.handle_side_passage(room, distance=30)
            elif 11 <= roll <=13:
                # Passage Turns
                self.handle_passage_turn(room)
            elif 14 <= roll <=16:
                # Chamber
                self.handle_chamber(room)
            elif roll ==17:
                # Stairs
                self.handle_stairs(room)
            elif roll ==18:
                # Dead End
                self.handle_dead_end(room)
            elif roll ==19:
                # Trick/Trap
                self.handle_trap(room)
            elif roll ==20:
                # Wandering Monster
                self.handle_wandering_monster(room)
            else:
                break  # Should not happen

            # For simplicity, break after one iteration. Remove or adjust as needed.
            break

    def handle_continue_straight(self, room, distance):
        # Create a corridor straight ahead
        corridor = self.create_corridor(room, direction='Straight', distance=distance)
        self.corridors[corridor.id] = corridor
        room.exits.append(Exit(direction='Straight', leads_to=corridor))
        # Process the corridor
        self.process_corridor(corridor)

    def handle_door(self, room):
        # Determine door location and what lies beyond
        location_roll = roll_die()
        if 1 <= location_roll <=6:
            location = 'Left'
            space = 'Parallel passage or 10x10 room'
        elif 7 <= location_roll <=12:
            location = 'Right'
            space = 'Passage straight ahead'
        elif 13 <= location_roll <=20:
            location = 'Ahead'
            space = 'Passage 45 degrees or Room/Chamber'
        # For simplicity, we'll just create a straight corridor
        corridor = self.create_corridor(room, direction=location, distance=30)
        self.corridors[corridor.id] = corridor
        room.exits.append(Exit(direction=location, leads_to=corridor))
        self.process_corridor(corridor)

    def handle_side_passage(self, room, distance):
        # Implement Table III: Side Passages
        side_roll = roll_die()
        if 1 <= side_roll <=2:
            direction = 'Left 90 degrees'
        elif 3 <= side_roll <=4:
            direction = 'Right 90 degrees'
        elif side_roll ==5:
            direction = 'Left 45 degrees ahead'
        elif side_roll ==6:
            direction = 'Right 45 degrees ahead'
        elif side_roll ==7:
            direction = 'Left 135 degrees'
        elif side_roll ==8:
            direction = 'Right 135 degrees'
        elif 9 <= side_roll <=10:
            direction = 'Left curve 45 degrees ahead'
        elif 11 <= side_roll <=13:
            direction = 'T intersection'
        elif 14 <= side_roll <=15:
            direction = 'Y intersection'
        elif 16 <= side_roll <=19:
            direction = 'Four-way intersection'
        elif side_roll ==20:
            direction = 'X intersection'
        else:
            direction = 'Straight'

        corridor = self.create_corridor(room, direction=direction, distance=distance)
        self.corridors[corridor.id] = corridor
        room.exits.append(Exit(direction=direction, leads_to=corridor))
        self.process_corridor(corridor)

    def handle_passage_turn(self, room):
        # Implement Table IV: Turns
        turn_roll = roll_die()
        if 1 <= turn_roll <=8:
            turn_direction = 'Left 90 degrees'
        elif 9 <= turn_roll <=10:
            turn_direction = 'Left 135 degrees'
        elif 11 <= turn_roll <=18:
            turn_direction = 'Right 90 degrees'
        elif turn_roll ==19:
            turn_direction = 'Right 45 degrees ahead'
        elif turn_roll ==20:
            turn_direction = 'Right 135 degrees'
        else:
            turn_direction = 'Straight'

        corridor = self.create_corridor(room, direction=turn_direction, distance=30)
        self.corridors[corridor.id] = corridor
        room.exits.append(Exit(direction=turn_direction, leads_to=corridor))
        self.process_corridor(corridor)

    def handle_chamber(self, room):
        # Implement Table V: Chambers and Rooms
        new_room = self.create_room(room.coordinates, self.level)
        self.rooms[new_room.id] = new_room
        room.exits.append(Exit(direction='Chamber', leads_to=new_room))
        self.process_room(new_room)

    def handle_stairs(self, room):
        # Implement Table VI: Stairs
        stairs_roll = roll_die()
        if 1 <= stairs_roll <=5:
            direction = 'Down 1 level'
            level_change = -1
        elif 6 <= stairs_roll <=7:
            direction = 'Down 2 levels'
            level_change = -2
        elif 8 <= stairs_roll <=9:
            direction = 'Down 3 levels'
            level_change = -3
        elif stairs_roll ==10:
            direction = 'Up 1 level'
            level_change = 1
        elif stairs_roll ==11:
            direction = 'Up dead end'
            level_change = None  # Special handling
        elif stairs_roll ==12:
            direction = 'Down dead end'
            level_change = None  # Special handling
        elif 13 <= stairs_roll <=14:
            direction = 'Chimney up 1 level'
            level_change = 1
        elif 15 <= stairs_roll <=16:
            direction = 'Chimney down 2 levels'
            level_change = -2
        elif 17 <= stairs_roll <=18:
            direction = 'Trap door down 1 level'
            level_change = -1
        elif 19 <= stairs_roll <=20:
            direction = 'Up 1 then down 2 levels'
            level_change = -1
        else:
            direction = 'No stairs'
            level_change = None

        if level_change and 1 <= self.level + level_change <= MAX_LEVEL:
            self.level += level_change
            stairs_info = {'from_room': room.id, 'to_level': self.level}
            self.stairs.append(stairs_info)
            # Create stairs as a special corridor
            corridor = self.create_corridor(room, direction=direction, distance=0)
            self.corridors[corridor.id] = corridor
            room.exits.append(Exit(direction=direction, leads_to=corridor))
            # Potentially link to another level
        else:
            # Handle dead end or special cases
            pass

    def handle_dead_end(self, room):
        # Dead end: no further processing
        pass

    def handle_trap(self, room):
        # Implement Table VII: Trick/Trap
        trap_roll = roll_die()
        # For simplicity, just note that a trap exists in the room
        room.contents += ", Trap"

    def handle_wandering_monster(self, room):
        # Implement wandering monster
        # For simplicity, just note that a monster is wandering
        room.contents += ", Wandering Monster"

    def create_corridor(self, room, direction, distance):
        corridor_id = next(id_gen)
        # Determine width from Table III.A
        width_roll = roll_die()
        if 1 <= width_roll <=12:
            width = 10
        elif 13 <= width_roll <=16:
            width = 20
        elif 17 <= width_roll <=18:
            width = 30
        elif 19 <= width_roll <=20:
            width = self.roll_table_iii_b()
        else:
            width = 10  # Default

        # Calculate end coordinates based on direction and distance
        start_x, start_y = room.coordinates[2], room.coordinates[3]  # Assuming exiting from top right
        if direction.startswith('Straight'):
            end_x = start_x + distance
            end_y = start_y
        elif 'Left' in direction:
            end_x = start_x
            end_y = start_y + distance
        elif 'Right' in direction:
            end_x = start_x
            end_y = start_y - distance
        else:
            end_x = start_x + distance
            end_y = start_y + distance

        end_coords = (end_x, end_y)
        corridor = Corridor('Passage', distance, width, direction, (start_x, start_y), end_coords, corridor_id, self.level)
        return corridor

    def roll_table_iii_b(self):
        # Implement Table III.B: Special Passage
        roll = roll_die()
        if 1 <= roll <=4:
            return 'Special: 40',  # Simplified
        elif 5 <= roll <=7:
            return 'Special: 40 double columns'
        elif 8 <= roll <=10:
            return 'Special: 50 double columns'
        elif 11 <= roll <=12:
            return 'Special: 50 columns with galleries'
        elif 13 <= roll <=15:
            return 'Special: 10 stream'
        elif 16 <= roll <=17:
            return 'Special: 20 river'
        elif 18 <= roll <=19:
            return 'Special: 40 river'
        elif roll ==20:
            return 'Special: 200 chasm'
        else:
            return 'Special: 10 stream'  # Default

    def process_corridor(self, corridor):
        # Process the corridor similar to a room
        pass  # Implement corridor processing if needed

    def save_dungeon(self):
        # Save the dungeon structure to a file
        dungeon_data = {
            'Rooms': [],
            'Corridors': [],
            'Stairs': self.stairs
        }
        for room in self.rooms.values():
            dungeon_data['Rooms'].append({
                'ID': room.id,
                'Type': room.type,
                'Shape': room.shape,
                'Size (sq ft)': room.size,
                'Coordinates': room.coordinates,
                'Exits': [{'Direction': exit.direction, 'LeadsTo': exit.leads_to.id} for exit in room.exits],
                'Contents': room.contents,
                'Level': room.level
            })
        for corridor in self.corridors.values():
            dungeon_data['Corridors'].append({
                'ID': corridor.id,
                'Type': corridor.type,
                'Length (ft)': corridor.length,
                'Width (ft)': corridor.width,
                'Direction': corridor.direction,
                'Start Coordinates': corridor.start_coords,
                'End Coordinates': corridor.end_coords,
                'Level': corridor.level
            })
        with open(self.dungeon_file, 'w') as f:
            json.dump(dungeon_data, f, indent=4)
        print(f"Dungeon saved to {self.dungeon_file}")

# Run the dungeon generator
if __name__ == "__main__":
    dungeon = Dungeon()
    dungeon.generate_dungeon()
