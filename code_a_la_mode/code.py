#Begin Imports
import sys
import math
#End Imports

#Begin Util Code
def log(x):
    print(x, file=sys.stderr)
    
# Cells
FLOOR_CELL = "."
EMPTY_TABLE = "#"
DISHWASHER = "D"
WINDOW = "W"
BLUEBERRIES_CRATE = "B"
ICE_CREAM_CRATE = "I"
STRAWBERRIES_CRATE = "S"
DOUGH_CRATE = "H"
CHOPPED_BOARD = "C"
OVEN = "O"

# Items
NONE = "NONE"
DISH = "DISH"
ICE_CREAM = "ICE_CREAM"
BLUEBERRIES = "BLUEBERRIES"
STRAWBERRIES = "STRAWBERRIES"
CHOPPED_STRAWBERRIES = "CHOPPED_STRAWBERRIES"
DOUGH = "DOUGH"
CROISSANT = "CROISSANT"
TART = "TART"
CHOPPED_DOUGH = "CHOPPED_DOUGH"
RAW_TART = "RAW_TART"


class Player:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.item = NONE
        self.has_chopped = False
        

class Tile:
    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.name = name
        self.item = None

    def parse_name(self):
        return self.name.split("-")

    def __repr__(self):
        return "Tile: " + str(self.x) + ", " + str(self.y)

    def __str__(self):
        return str(self.x) + "." + str(self.y)
        
    def wall_hack_distance(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y)
        
class Client:
    def __init__(self, request, reward):
        self.dish_nb = 0
        self.want_ice_cream = False
        self.want_straw = False
        self.want_blue = False
        self.want_croissant = False
        self.want_tart = False
        self.request = request
        self.extract_plate_nb (request)
        self.reward = reward
        
    def extract_plate_nb(self, request):
        if ICE_CREAM in request:
            self.dish_nb = self.dish_nb + 1
            self.want_ice_cream = True
        if BLUEBERRIES in request:
            self.dish_nb = self.dish_nb + 1
            self.want_blue = True
        if STRAWBERRIES in request:
            self.dish_nb = self.dish_nb + 1
            self.want_straw = True
        if CROISSANT in request:
            self.dish_nb = self.dish_nb + 1
            self.want_croissant = True
        if TART in request:
            self.dish_nb = self.dish_nb + 1
            self.want_tart = True
    
    def rating(self):
        if self.want_tart:
            return self.reward / (4 * self.dish_nb)
        if self.want_croissant:
            return self.reward / (2 * self.dish_nb)
        return self.reward / self.dish_nb
        
    def __repr__(self):
        return "Client : want " + str(self.request) + ", for " + str(self.reward) + " (adjusted = " + str(self.rating()) + ")"


class Game:
    def __init__(self):
        self.player = Player()
        self.partner = Player()
        self.tiles = []
        self.clients = []
        self.retained_client = None

    def addTile(self, x, y, tileChar):
        if tileChar != '.':
            self.tiles.append(Tile(x, y, tileChar))

    def getTileByName(self, name):
        for t in self.tiles:
            if t.name == name:
                return t
        #If tile not found
        log("Error: Tile not found in function getTileByName")
        return None
        
    def getNearestTileByName(self, name):
        max_dist = 16
        nearest = self.getTileByName(name)
        for t in self.tiles:
            dist = t.wall_hack_distance(self.player)
            if dist < max_dist and t.name == name and t.item == None:
                nearest = t
                max_dist = dist
        return nearest

    def getTileByItem(self, item):
        for t in self.tiles:
            if t.item == item:
                return t
        #If tile not found
        log("Error: Tile not found in function getTileByItem")
        return None
    

    def getTileByCoords(self, x, y):
        for t in self.tiles:
            if t.x == x and t.y == y:
                return t
        #If tile not found
        log("Error: Tile not found in function getTileByCoords")

    def updatePlayer(self, x, y, item):
        self.player.x = x
        self.player.y = y
        self.player.item = item

    def updatePartner(self, x, y, item):
        self.partner.x = x
        self.partner.y = y
        self.partner.item = item
        
    def addClient(self, client):
        self.clients.append(client)
        
    def clearClient(self):
        self.clients = []
        
    def oneClientDoesntWantStraw(self):
        value = False
        for client in self.clients:
            value = value or not client.want_straw
        return value

    def use(self, tile, text):
        print("USE", tile.x, tile.y, text)

    def move(self, tile):
        print("MOVE", tile.x, tile.y)
        
    def move(self, x, y):
        print("MOVE", x, y)
        
    def wait(self):
        print("WAIT")
        
#End Util code

#Begin game code
game = Game()

# ALL CUSTOMERS INPUT: to ignore until bronze
num_all_customers = int(input())
for i in range(num_all_customers):
    # customer_item: the food the customer is waiting for
    # customer_award: the number of points awarded for delivering the food
    customer_item, customer_award = input().split()
    customer_award = int(customer_award)

# KITCHEN INPUT
for y in range(7):
    kitchen_line = input()
    for x, tileChar in enumerate(kitchen_line):
        game.addTile(x, y, tileChar)

# game loop
while True:
    game.clearClient()
    
    turns_remaining = int(input())

    # PLAYERS INPUT
    #Gather and update player information
    player_x, player_y, player_item = input().split()
    player_x = int(player_x)
    player_y = int(player_y)
    game.updatePlayer(player_x, player_y, player_item)

    #Gather and update partner information
    partner_x, partner_y, partner_item = input().split()
    partner_x = int(partner_x)
    partner_y = int(partner_y)
    game.updatePartner(partner_x, partner_y, partner_item)

    #Gather and update table information
    for t in game.tiles:
        t.item = None
    num_tables_with_items = int(input())  # the number of tables in the kitchen that currently hold an item
    for i in range(num_tables_with_items):
        table_x, table_y, item = input().split()
        table_x = int(table_x)
        table_y = int(table_y)
        game.getTileByCoords(table_x, table_y).item = item

    # oven_contents: ignore until bronze league
    oven_contents, oven_timer = input().split()
    oven_timer = int(oven_timer)
    num_customers = int(input())  # the number of customers currently waiting for food
    for i in range(num_customers):
        customer_item, customer_award = input().split()
        customer_award = int(customer_award)
        game.addClient(Client(customer_item, customer_award))

    # GAME LOGIC
    # V2
    clients_to_serve = sorted(game.clients, key=lambda cli: cli.rating())
    if game.retained_client == None:
        game.retained_client = clients_to_serve[1]
        
    log("Selected client request => " + game.retained_client.request + " - for " + str(game.retained_client.reward))
    
    if CROISSANT in game.retained_client.request and CROISSANT not in game.player.item and game.getTileByItem(CROISSANT) == None:
        log("oven contains :" + str(oven_contents))
        if "NONE" in str(oven_contents):
            if DOUGH not in game.player.item:
                game.use(game.getTileByName(DOUGH_CRATE), "get dough !")
            else:
                game.use(game.getTileByName(OVEN), "get hot !")
        elif CROISSANT in str(oven_contents):
            game.use(game.getTileByName(OVEN), "get croissant !")
        else:
            game.wait()
            
    elif CHOPPED_STRAWBERRIES in game.retained_client.request and CHOPPED_STRAWBERRIES not in game.player.item:
        if CROISSANT in game.player.item:
            game.use(game.getNearestTileByName(EMPTY_TABLE), "Don't touch this")
        elif STRAWBERRIES not in game.player.item:
            game.use(game.getTileByName(STRAWBERRIES_CRATE), "Grab a strawberry ?")
        elif CHOPPED_STRAWBERRIES in game.player.item:
            game.use(game.getNearestTileByName(EMPTY_TABLE), "Dobby a terminer, maître")
        else:
            game.use(game.getTileByName(CHOPPED_BOARD), "Chop chop")
            
    else:
        if DISH not in game.player.item:
            game.use(game.getTileByName(DISHWASHER), "you wash it")
        
        elif game.getTileByItem(CROISSANT) != None and CROISSANT not in game.player.item:
            game.use(game.getTileByItem(CROISSANT), "get back here")
            
        elif ICE_CREAM in game.retained_client.request and ICE_CREAM not in game.player.item:
            game.use(game.getTileByName(ICE_CREAM_CRATE), "It's cold outside")
            
        elif BLUEBERRIES in game.retained_client.request and BLUEBERRIES not in game.player.item:
            game.use(game.getTileByName(BLUEBERRIES_CRATE), "I'm blue")
            
        else:
            game.retained_client = None
            game.use(game.getTileByName(WINDOW), "Travail termine")
            
    
    # V1 (ignore client reward...)
    #if game.oneClientDoesntWantStraw() or CHOPPED_STRAWBERRIES in game.player.item:
    #    if DISH not in game.player.item:
    #        game.use(game.getTileByName(DISHWASHER), "you wash it")
    #    elif ICE_CREAM not in game.player.item:
    #        game.use(game.getTileByName(ICE_CREAM_CRATE), "It's cold outside")
    #    elif BLUEBERRIES not in game.player.item:
    #        game.use(game.getTileByName(BLUEBERRIES_CRATE), "I'm blue")
    #    else:
    #        game.use(game.getTileByName(WINDOW), "Travail term")
    #        
    #elif game.getTileByItem(CHOPPED_STRAWBERRIES) != None and STRAWBERRIES not in game.player.item:
    #    game.use(game.getTileByItem(CHOPPED_STRAWBERRIES), "get chopped !!")
    #    
    #elif BLUEBERRIES in game.player.item or ICE_CREAM in game.player.item:
    #    game.use(game.getTileByName(WINDOW), "Drop it likes it hot")
    #    
    #else:
    #    if STRAWBERRIES not in game.player.item:
    #        game.use(game.getTileByName(STRAWBERRIES_CRATE), "Grab a cherry ?")
    #    elif CHOPPED_STRAWBERRIES in game.player.item:
    #        game.use(game.getNearestTileByName(EMPTY_TABLE), "Dobby a terminer, maître")
    #    else:
    #        game.use(game.getTileByName(CHOPPED_BOARD), "Chop chop")
#End game code
