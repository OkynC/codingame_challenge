import sys
import math
import copy
import itertools
import numpy
from collections import namedtuple
from heapq import *
import timeit


# Survive the wrath of Kutulu
# Coded fearlessly by JohnnyYuge & nmahoude (ok we might have been a bit scared by the old god...but don't say anything)



def debug (text):
    print (text, file=sys.stderr)

Path = namedtuple ("Path", "estimated_cost tie_breaker path")
Position = namedtuple ("position", "x, y")

# classes used to define maze topology
#########################################
class Maze():
    def __init__ (self, width, heght):
        self.cells = [[Cell (x,y) for y in range(height)] for x in range(width)]
        # aliased collection for quick access to a specific type of room
        self.rooms = []
        self.spawners = []
        
    def set_row (self, row_number, serialized_row_string):
        column_number = 0
        for char in serialized_row_string:
            if char == 'w':   
                self.cells [column_number][row_number] = Spawner (column_number, row_number)
            elif char == '.' or char == 'U':
                self.cells [column_number][row_number] = Room (column_number, row_number)
            # no else, empty cells are the default             
            column_number += 1 
    
    def compute_maze_properties (self):
        """
        analyze maze and build metadata such as adjacent cell, shortest path info etc...
        """
        self.rooms = [cell for cell in itertools.chain.from_iterable (self.cells) if isinstance(cell, Room)]
        self.spawner = [cell for cell in itertools.chain.from_iterable (self.cells) if isinstance(cell, Spawner)]
        for room in self.rooms:
            # not optimized but it doesnt matter, we have 1 sec to do the processing
            for adjacent_room_maybe in self.rooms:
                if room.is_adjacent (adjacent_room_maybe):
                    room.add_adjacent_room (adjacent_room_maybe)
    
    def get_cell_pos (self, x, y):
        return self.cells [x][y]
    
    def get_cell (self, entity):
        return self.cells [entity.pos.x][entity.pos.y]
        
    def get_adjacent_positions (self, entity):
        return [cell.position for cell in self.cells [entity.pos.x][entity.pos.y].get_adjacent_rooms()]   
    
    def get_wall_hack_distance (self, entity1, entity2):
        return self.get_cell (entity1).wall_hack_distance (self.get_cell (entity2))
    
    def los_between (self, entity1, entity2):
        cell_between_entities = self.get_shortest_path (entity1, entity2)
        x_different_entities = [cell.position.x != entity1.pos.x for cell in cell_between_entities]
        y_different_entities = [cell.position.y != entity1.pos.y for cell in cell_between_entities]
        return x_different_entities or y_different_entities
    
    def get_shortest_path (self, entity1, entity2):
        # alias for data
        start_cell = self.get_cell (entity1)
        end_cell = self.get_cell (entity2)
        # to break tie in case of equal cost path
        path_searched_count = 0
        # A*/djikstra algo
        pending_paths_heap = [Path (0, 0, [start_cell])]
        heapify (pending_paths_heap)
        seen_rooms = set()
        while pending_paths_heap:
            path_data = heappop (pending_paths_heap)
            current_room = path_data.path [-1]
            if current_room == end_cell:
                return path_data.path
            current_cost = path_data.estimated_cost
            if not current_room in seen_rooms:
                seen_rooms.add (current_room)
                for adjacent_room in [room for room in current_room.get_adjacent_rooms() if room not in seen_rooms]:
                    next_path = path_data.path + [adjacent_room]
                    next_cost = len (next_path) + current_room.wall_hack_distance (end_cell)
                    path_searched_count += 1
                    next_path_data = Path (estimated_cost = next_cost, tie_breaker = path_searched_count, path = next_path)
                    heappush (pending_paths_heap, next_path_data)   

class Cell ():
    def __init__ (self, x , y):
        self.position = Position (x, y)
    
    def wall_hack_distance (self, other):
        return abs(self.position.x - other.position.x) + abs(self.position.y - other.position.y)
    
    def is_adjacent (self, other):
        return self.wall_hack_distance (other) == 1

class Room (Cell):
    def __init__ (self, x, y):
        super().__init__ (x, y)
        self.adjacent_rooms = []
    
    def add_adjacent_room (self, room):
        self.adjacent_rooms.append (room)
        
    def get_adjacent_rooms (self):
        return self.adjacent_rooms + [self]

class Spawner (Room):
    def __init__ (self, x, y):
        super().__init__ (x, y)
########### end maze


class Position:
    
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y
    
    def update (self, x, y):
        """
        Udpate value for Position
        """
        self.x = x
        self.y = y
    
    def __sub__ (self, other):
        """
        Define "-" operator for class
        """
        return Position (self.x - other.x, self.y - other.y)
    
    def __add__ (self, other):
        """
        Define "-" operator for class
        """
        return Position (self.x + other.x, self.y + other.y)
        
    def __abs__ (self):
        """
        Define abs() function for class
        """
        return Position (abs(self.x), abs(self.y))
        
    def __le__ (self, other):
        """
        Define "<=" operator for class
        """
        return self.x <= other.x and self.y <= other.y
    
    def __eq__ (self, other):
        """
        Define "==" operator for class
        """
        if other != None:
            return self.x == other.x and self.y == other.y
        return False
        
    def __str__ (self):
        """
        Define str() function for class
        """
        return "{} {}".format(int (self.x), int (self.y))


class Entity:
    
    def __init__(self):
        self.kind  = ""
        self.ident = 0
        self.pos   = Position()
    
    def update(self, kind, ident, x, y):
        self.kind  = kind
        self.ident = ident
        self.pos.update (x, y)
    
    def get_nearest(self, others):
        """
        Wrong way to find nearest entity => does not work correctly
        """
        nearest = None
        current_val = Position (18, 18)
        for _key,entity in others.items():
            debug("Entity {}, is at {}".format(entity.ident, entity.pos))
            if abs(entity.pos - self.pos) <= abs(current_val - self.pos):
                current_val = entity.pos
                nearest     = entity
        return nearest
            
    def is_on_cell (self, cell):
        return self.pos == cell

    #def get_nearest(self, maze, other_entity):
    #    return maze.get_shortest_path (self, other_entity)

class Effect(Entity):
    
    def __init__(self):
        Entity.__init__(self)
        self.kind = "Effect"
        self.time_to_end = 0
        self.launcher = 0
    
    def update (self, x, y, param_0, param_1, param_2):
        self.ident = -1
        self.pos.update (x, y)
        self.time_to_end = param_0
        self.launcher = param_1
    
    def __str__(self):
        return "Effect pos : {}".format (self.pos)

class Light(Effect):
    pass

class Map(Effect):
    pass

class Yell(Effect):
    pass

class Shelter(Effect):
    pass

class Explorer(Entity):
    
    def __init__(self):
        Entity.__init__(self)
        self.kind          = "Explorer"
        self.mental_health = 250
        self.plan_use      = 2
        self.torch_use     = 3
    
    def update (self, x, y, param_0, param_1, param_2):
        self.pos.update (x, y)
        self.mental_health = param_0
        self.plan_use      = param_1
        self.torch_use     = param_2
    
    def can_draw_plan (self):
        if self.plan_use > 0:
            return True
        return False
    
    def can_light_torch (self):
        if self.torch_use > 0:
            return True
        return False
    
    def is_subject_to_effect(self, effect_list):
        val = False
        for effect in effect_list:
            if effect == Map():
                if abs(effect.pos - self.pos) <= 2:
                    val = True
            elif effect == Light():
                if abs(effect.pos - self.pos) <= 5:
                    val = True
        return val
    
    def is_minion_nearer (self, other, minion):
        return abs(my_Explorer.pos - minion.pos) <= abs(my_Explorer.pos - other.pos)
    
    def can_be_targetted(self, other, map_to_consider):
        target = None
        
        if self.pos == other.pos:
            pass #do nothing => other is on self

        elif abs(self.pos - other.pos) <= Position (1, 1):
            pass # do nothing, other is near self

        else:
            # other try to reach self
            # self and other are on same line
            if self.pos.x == other.pos.x:
                if map_to_consider [other.pos.y + 1][other.pos.x] == '.' or map_to_consider [other.pos.y - 1][other.pos.x] == '.':
                    target = self.pos
                else:
                    debug ("cannot reach self u/d")
            
            # self and other are on same column
            elif self.pos.y == other.pos.y:
                if map_to_consider [other.pos.y][other.pos.x - 1] == '.' or map_to_consider [other.pos.y][other.pos.x + 1] == '.':
                    target = self.pos
                else:
                    debug ("cannot reach self l/r")
            
            # self and other are on distinct row and line
            else:
                if self.pos.x > other.pos.x:
                    if map_to_consider [other.pos.y][other.pos.x + 1] == ".":
                        target = Position (other.pos.x + 1, other.pos.y)
                    elif map_to_consider [other.pos.y + 1][other.pos.x] == ".":
                        target = Position (other.pos.x, other.pos.y + 1)
                    elif map_to_consider [other.pos.y - 1][other.pos.x] == ".":
                        target = Position (other.pos.x, other.pos.y - 1)
                    else:
                        debug ("cannot reach...")
                        
                elif self.pos.x < other.pos.x:
                    if map_to_consider [other.pos.y][other.pos.x - 1] == ".":
                        target = Position (other.pos.x - 1, other.pos.y)
                    elif map_to_consider [other.pos.y + 1][other.pos.x] == ".":
                        target = Position (other.pos.x, other.pos.y + 1)
                    elif map_to_consider [other.pos.y - 1][other.pos.x] == ".":
                        target = Position (other.pos.x, other.pos.y - 1)
                    else:
                        debug ("cannot reach...")

        return target
        
    def wall_hack_distance (self, other, maze):
        return maze.get_wall_hack_distance (self, other)
    
    

class Minion(Entity):
    
    def __init__(self):
        Entity.__init__(self)
        self.kind = "Minions"
        self.invoc_time  = 0
        self.recall_time = 0
        self.state       = 0
        self.target      = 0
    
    def is_spawning (self):
        return self.state == 0

    def update (self, ident, x, y, param_0, param_1, param_2):
        self.ident = ident
        self.pos.update (x, y)
        self.state = param_1
        if self.is_spawning():
            self.invoc_time  = param_0
            self.recall_time = 0
        else:
            self.invoc_time  = 0
            self.recall_time = param_0
        self.target = param_2
    
    def is_on_map(self):
        return self.recall_time > 0

class Wanderer(Minion):
    pass

class Slasher(Minion):
    pass


def check_pos_is_safe (pos_to_check, minion_dict, level):
    pos_is_safe = True
    
    if not isinstance (level.get_cell_pos (pos_to_check.x, pos_to_check.y), Room):
        return False
    
    for _key, minion in minion_dict.items():
        if minion.is_on_cell (pos_to_check):
            if minion.state != 0:
                pos_is_safe = False
        if minion.is_on_cell (Position (pos_to_check.x, pos_to_check.y + 1)):
            if minion.state != 0:
                pos_is_safe = False
        if minion.is_on_cell (Position (pos_to_check.x, pos_to_check.y - 1)):
            if minion.state != 0:
                pos_is_safe = False
        if minion.is_on_cell (Position (pos_to_check.x + 1, pos_to_check.y)):
            if minion.state != 0:
                pos_is_safe = False
        if minion.is_on_cell (Position (pos_to_check.x - 1, pos_to_check.y)):
            if minion.state != 0:
                pos_is_safe = False

    return pos_is_safe


# Get map data
width     = int(input())
height    = int(input())
level_map = []
maze      = Maze (width, height)
for i in range(height):
    raw_in = input()
    level_map.append (raw_in)
    maze.set_row (i, raw_in)
    
maze.compute_maze_properties()

debug (level_map)

# sanity_loss_lonely: how much sanity you lose every turn when alone, always 3 until wood 1
# sanity_loss_group: how much sanity you lose every turn when near another player, always 1 until wood 1
# wanderer_spawn_time: how many turns the wanderer take to spawn, always 3 until wood 1
# wanderer_life_time: how many turns the wanderer is on map after spawning, always 40 until wood 1
sanity_loss_lonely, sanity_loss_group, wanderer_spawn_time, wanderer_life_time = [int(i) for i in input().split()]

# Create creatures (4 explorer and list of minions)
my_Explorer = Explorer()


# game loop
while True:
    
    explorer_dict = {}
    minions_dict  = {}
    effect_list = []

    # Get turn data
    entity_count = int(input())  # the first given entity corresponds to your explorer
    for i in range(entity_count):
        entity_type, ident, x, y, param_0, param_1, param_2 = input().split()
        ident = int(ident)
        x = int(x)
        y = int(y)
        param_0 = int(param_0)
        param_1 = int(param_1)
        param_2 = int(param_2)
        if entity_type == "EXPLORER":
            if i == 0:
                my_Explorer.update (x, y, param_0, param_1, param_2)
                my_Explorer.ident = ident

            else:
                if explorer_dict.get (ident) == None:
                    explorer_dict [ident] = Explorer()
                explorer_dict [ident].ident = ident
                explorer_dict [ident].update (x, y, param_0, param_1, param_2)
        
        elif entity_type == "WANDERER":
            if minions_dict.get (ident) == None:
                minions_dict [ident] = Wanderer()
            minions_dict [ident].update (ident, x, y, param_0, param_1, param_2)
            
        elif entity_type == "SLASHER":
            if minions_dict.get (ident) == None:
                minions_dict [ident] = Slasher()
            minions_dict [ident].update (ident, x, y, param_0, param_1, param_2)
        
        elif entity_type == "EFFECT_PLAN":
            new_Effect = Map()
            new_Effect.update (x, y, param_0, param_1, param_2)
            effect_list.append (new_Effect)

        elif entity_type == "EFFECT_LIGHT":
            new_Effect = Light()
            new_Effect.update (x, y, param_0, param_1, param_2)
            effect_list.append (new_Effect)
        
        elif entity_type == "EFFECT_SHELTER":
            new_Effect = Shelter()
            new_Effect.update (x, y, param_0, param_1, param_2)
            effect_list.append (new_Effect)

        elif entity_type == "EFFECT_YELL":
            new_Effect = Yell()
            new_Effect.update (x, y, param_0, param_1, param_2)
            effect_list.append (new_Effect)
    
    debug (effect_list)
    
    target = None
    nearest_minion = None
    
    nearest_explorer = None
    shortest_path  = 1000
    for _key, explorer in explorer_dict.items():
        path = maze.get_shortest_path (explorer, my_Explorer)
        new_path = len(path)
        if new_path < shortest_path and path != None:
            shortest_path    = new_path
            nearest_explorer = explorer
        
    if nearest_explorer != None:
        path = maze.get_shortest_path (nearest_explorer, my_Explorer)
        if path != None:
            if check_pos_is_safe (path[0].position, minions_dict, maze):
                target = nearest_explorer.pos
        debug ("Nearest explorer is {}".format(nearest_explorer.ident))
    else:
        debug ("No nearest explorer")
    
    shortest_path  = 1000
    for _key, minion in minions_dict.items():
        path = maze.get_shortest_path (minion, my_Explorer)
        new_path = len (path)
        if new_path < shortest_path:
            shortest_path = new_path
            nearest_minion = minion
            
    if nearest_minion != None:
        debug ("Nearest minion is {}".format(nearest_minion.ident))
    else:
        debug ("No nearest minion")
    
    if nearest_minion != None:
        possible_target = []
        if nearest_minion.pos.x == my_Explorer.pos.x:
            if nearest_minion.pos.y == (my_Explorer.pos.y - 1):
                # check nearby position (opposite to minion to flee)
                # first next
                # then 1 beyond
                if check_pos_is_safe (Position (my_Explorer.pos.x, my_Explorer.pos.y + 1), minions_dict, maze):
                    debug ("This position is safe {}".format (Position (my_Explorer.pos.x, my_Explorer.pos.y + 1)))
                    target = Position (my_Explorer.pos.x, my_Explorer.pos.y + 1)

                elif check_pos_is_safe (Position (my_Explorer.pos.x - 1, my_Explorer.pos.y), minions_dict, maze):
                    debug ("This position is safe {}".format (Position (my_Explorer.pos.x - 1, my_Explorer.pos.y)))
                    target = Position(my_Explorer.pos.x - 1, my_Explorer.pos.y)
                    
                elif check_pos_is_safe (Position (my_Explorer.pos.x + 1, my_Explorer.pos.y), minions_dict, maze):
                    debug ("This position is safe {}".format (Position (my_Explorer.pos.x + 1, my_Explorer.pos.y)))
                    target = Position(my_Explorer.pos.x + 1, my_Explorer.pos.y)
                    
                else:
                    debug ("We are trapped 1")
                
            elif nearest_minion.pos.y == (my_Explorer.pos.y + 1):
                if check_pos_is_safe (Position (my_Explorer.pos.x, my_Explorer.pos.y - 1), minions_dict, maze):
                    target = Position (my_Explorer.pos.x, my_Explorer.pos.y - 1)

                elif check_pos_is_safe (Position (my_Explorer.pos.x - 1, my_Explorer.pos.y), minions_dict, maze):
                    target = Position(my_Explorer.pos.x - 1, my_Explorer.pos.y)
                    
                elif check_pos_is_safe (Position (my_Explorer.pos.x + 1, my_Explorer.pos.y), minions_dict, maze):
                   target = Position(my_Explorer.pos.x + 1, my_Explorer.pos.y)
                else:
                    debug ("We are trapped 2")
            
        elif nearest_minion.pos.y == my_Explorer.pos.y:
            if nearest_minion.pos.x == (my_Explorer.pos.x + 1):
                if check_pos_is_safe (Position (my_Explorer.pos.x - 1, my_Explorer.pos.y), minions_dict, maze):
                    target = Position (my_Explorer.pos.x - 1, my_Explorer.pos.y)

                elif check_pos_is_safe (Position (my_Explorer.pos.x, my_Explorer.pos.y - 1), minions_dict, maze):
                    target = Position(my_Explorer.pos.x, my_Explorer.pos.y - 1)
                    
                elif check_pos_is_safe (Position (my_Explorer.pos.x, my_Explorer.pos.y + 1), minions_dict, maze):
                   target = Position(my_Explorer.pos.x, my_Explorer.pos.y + 1)
                   
                else:
                    debug ("We are trapped 3")
            
            elif nearest_minion.pos.x == (my_Explorer.pos.x - 1):
                if check_pos_is_safe (Position (my_Explorer.pos.x + 1, my_Explorer.pos.y), minions_dict, maze):
                    target = Position (my_Explorer.pos.x + 1, my_Explorer.pos.y)

                elif check_pos_is_safe (Position (my_Explorer.pos.x, my_Explorer.pos.y - 1), minions_dict, maze):
                    target = Position(my_Explorer.pos.x, my_Explorer.pos.y - 1)
                    
                elif check_pos_is_safe (Position (my_Explorer.pos.x, my_Explorer.pos.y + 1), minions_dict, maze):
                   target = Position(my_Explorer.pos.x, my_Explorer.pos.y + 1)
                   
                else:
                    debug ("We are trapped 4")
    
    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)
    # MOVE <x> <y> | WAIT
    debug ("target = {} - mental_health = {} - is_subject = {}".format(target, my_Explorer.mental_health, my_Explorer.is_subject_to_effect (effect_list)))
    if target != None:
        print ("MOVE {} {}".format (target.x, target.y))
    else:
        if my_Explorer.mental_health < 150 and not my_Explorer.is_subject_to_effect (effect_list):
            print ("PLAN Lets make a map")
        else:
            print ("WAIT")
    
    