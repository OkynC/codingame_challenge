import sys
import math

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.


def debug(text):
    print(text, file=sys.stderr)

class Card:
    
    def __init__(self, id, mana_cost, card_number):
        self.id = id
        self.mana_cost = mana_cost
        self.card_number = card_number
        self.weight = 0
    
    def __str__(self):
        return "Card id {} with:\nratio = {}".format (self.id, self.weight)

class Creature(Card):
    
    def __init__(self, id, mana_cost, attack, defense, capa, card_number, mhc, ohc):
        super(Creature, self).__init__(id, mana_cost, card_number)
        self.attack = attack
        self.defense = defense
        if mana_cost > 0:
            if card_number in [30, 69, 80, 99, 103, 105]: # Must take those cards
                self.weight = 100
            elif card_number in [45, 25, 53]: # Must NOT take those cards
                self.weight = -100
            elif attack == 0: # Refuse cards with 0 attack
                self.weight = -100
            else: # Calcul the value ratio of the card
                self.weight = 0
                
                if mana_cost > 6: # Avoid cards with man cost over 6 => no time to play them
                    self.weight -= (0.3 * (mana_cost - 6))
                    
                if "G" in capa: # For guard cards, take defense and attack in ratio
                    self.weight += 0.2
                    
                    if "W" in capa: # Guard with Ward are very nice
                        self.weight += 0.5

                if "W" in capa:
                    self.weight += 1
                    
                if "L" in capa:
                    self.weight += 0.5
                    
                if "D" in capa:
                    self.weight += (0.2 * attack)
                
                if "C" in capa:
                    self.weight += 0.2
                    
                if "B" in capa:
                    self.weight += 0.3
                
                if mhc >= 0:
                    self.weight += (0.2 * mhc)
                else:
                    self.weight += (0.4 * mhc)
                    
                if ohc > 0:
                    self.weight += (-0.4 * ohc)
                else:
                    self.weight += (-0.2 * ohc)
                
                # Defense bonus
                ratio_d = defense - mana_cost
                if ratio_d < 0:
                    ratio_d *= 2
                self.weight += ratio_d
                    
                # Attack bonus
                ratio_a = attack - mana_cost
                if ratio_a < 0:
                    ratio_a *= 2
                
                self.weight += ratio_a
        else:
            self.weight = 0
        self.capa = capa
        
        def __str__(self):
            return "Creature {} with ratio {}".format (self.id, self.weight)

class Object(Card):
    
    def __init__(self, id, mana_cost, attack, defense, capa, color, card_number, mhc, ohc):
        super(Object, self).__init__(id, mana_cost, card_number)
        self.bonus_att = attack
        self.bonus_def = defense
        if card_number in [137, 138, 139, 140, 158]:
            self.weight = -100
        elif "r" in color: # Red object target opponent creatures
            self.weight = -4
            
        elif "g" in color: # green object target my creature
            self.weight = 0
            
            if mana_cost > 6: # Avoid cards with man cost over 6 => no time to play them
                self.weight -= (0.3 * (mana_cost - 5))
            
            if "G" in capa:
                self.weight += 0.5
            
            if "B" in capa:
                self.weight += 0.2 * attack
                
            # Defense bonus
            ratio_d = defense - (mana_cost - 1)
            if ratio_d < 0:
                ratio_d *= 2
            self.weight += ratio_d
                
            # Attack bonus
            ratio_a = attack - (mana_cost - 1)
            if ratio_a < 0:
                ratio_a *= 2
            
            self.weight += ratio_a

        else: # Blue item target all
            self.weight = 0
            
            if mhc > 0:
                self.weight += (0.2 * (mhc - mana_cost))
            if mhc == 0:
                self.weight += 0
            else:
                self.weight -= 2
                
            if ohc > 0:
                self.weight -= 2
            if ohc == 0:
                self.weight += 0
            else:
                self.weight += (-0.2 * (ohc - mana_cost))
        
        self.capa = capa
        self.color = color

class Player:
    
    def __init__(self):
        health = 0
        mana = 0
        runes = 0
        card_nb = 0
        deck = []
    
    def update(self, health, mana, card_nb, rune):
        self.health = health
        self.mana = mana
        self.runes = rune
        self.card_nb = card_nb

my_cards = {}
my_objects = {}
my_played_cards = {}
opponent_played_cards = {}
draft_cards = {}

me = Player()
opponent = Player()

# game loop
while True:
    
    # Get my info
    player_health, player_mana, player_deck, player_rune = [int(j) for j in input().split()]
    me.update (player_health, player_mana, player_deck, player_rune)

    # Get opponent info
    player_health, player_mana, player_deck, player_rune = [int(j) for j in input().split()]
    opponent.update (player_health, player_mana, player_deck, player_rune)

    opponent_hand = int(input())
    card_count = int(input())

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)
    if me.mana == 0:
        # Draft phase
        for i in range(card_count):
            card_number, instance_id, location, card_type, cost, attack, defense, abilities, my_health_change, opponent_health_change, card_draw = input().split()
            card_number = int(card_number)
            instance_id = int(instance_id)
            location = int(location)
            card_type = int(card_type)
            cost = int(cost)
            attack = int(attack)
            defense = int(defense)
            my_health_change = int(my_health_change)
            opponent_health_change = int(opponent_health_change)
            card_draw = int(card_draw)
            
            if card_type == 0:
                new_card = Creature(i, cost, attack, defense, abilities, card_number, my_health_change, opponent_health_change)
            else:
                if card_type == 1:
                    color = "g"
                elif card_type == 2:
                    color = "r"
                elif card_type == 3:
                    color = "b"
                else:
                    color = ""
                new_card = Object(i, cost, attack, defense, abilities, color, card_number, my_health_change, opponent_health_change)
            draft_cards [i] = new_card
        
        sorted_by_value = sorted(draft_cards.items(), key=lambda x : x[1].weight)
        debug(sorted_by_value)
        for _k, card in draft_cards.items():
            debug(str(card))
        print("PICK {}".format (sorted_by_value.pop()[1].id))
        
    else:
        my_cards.clear()
        my_played_cards.clear()
        opponent_played_cards.clear()
        my_objects.clear()
        nb_played = 0
        
        # Battle phase
        for i in range(card_count):
            card_number, instance_id, location, card_type, cost, attack, defense, abilities, my_health_change, opponent_health_change, card_draw = input().split()
            card_number = int(card_number)
            instance_id = int(instance_id)
            location = int(location)
            card_type = int(card_type)
            cost = int(cost)
            attack = int(attack)
            defense = int(defense)
            my_health_change = int(my_health_change)
            opponent_health_change = int(opponent_health_change)
            card_draw = int(card_draw)
            
            if card_type == 0:
                new_card = Creature(instance_id, cost, attack, defense, abilities, card_number, my_health_change, opponent_health_change)
            else:
                if card_type == 1:
                    color = "v"
                elif card_type == 2:
                    color = "r"
                elif card_type == 3:
                    color = "b"
                else:
                    color = ""
                new_card = Object(instance_id, cost, attack, defense, abilities, color, card_number, my_health_change, opponent_health_change)
            
            if location == 0:
                if isinstance(new_card, Object):
                    my_objects [instance_id] = new_card
                else:
                    my_cards [instance_id] = new_card
            elif location == 1:
                my_played_cards [instance_id] = new_card
                nb_played = nb_played + 1
            elif location == -1:
                opponent_played_cards [instance_id] = new_card
                
        sorted_by_value = sorted(my_cards.items(), key=lambda x : x[1].weight)
        
        actions = ""
        last_summoned = 0
        # Summon all creature if possible
        if nb_played < 6:
            for tupple in sorted_by_value:
                if isinstance(tupple[1], Creature):
                    if tupple[1].mana_cost <= me.mana:
                        actions = actions + str("SUMMON {};".format(tupple[1].id))
                        me.mana = me.mana - tupple[1].mana_cost
                        last_summoned = tupple[1].id
                        nb_played = nb_played + 1
                        if "C" in tupple[1].capa:
                            my_played_cards [tupple[0]] = tupple[1]
                        del my_cards[tupple[0]]
        else:
            debug ("No room")
        
        # Try to use an object if mana available
        for k, v in my_objects.items():
            if v.mana_cost <= me.mana:
                if v.color in "b":
                    actions = actions + str("USE {} -1;".format(k))
                    me.mana -= v.mana_cost
                elif v.color in "v" and last_summoned != 0:
                    actions = actions + str("USE {} {};".format(k, last_summoned))
                    me.mana -= v.mana_cost
                elif v.color in "r":
                    debug("do not use red object")

        # Check if an opponent creature has guard
        list_of_guards = []
        for k, v in opponent_played_cards.items():
            if "G" in v.capa:
                list_of_guards.append(k)
            elif v.card_number in [14]:
                list_of_guards.append(k)
                
        # Attack with creatures (guards then player)
        for k, v in my_played_cards.items():
            if list_of_guards != None and list_of_guards:
                current = list_of_guards[0]
                actions += str("ATTACK {} {};".format (k, current))
                if not ("W" in opponent_played_cards[current].capa):
                    if opponent_played_cards[current].defense <= v.attack or "L" in v.capa:
                        # remove guard from list
                        if len(list_of_guards) > 1:
                            list_of_guards = list_of_guards[-1:]
                        else:
                            list_of_guards = []
                else:
                    opponent_played_cards[current].defense = opponent_played_cards[current].defense - v.attack
            else:
                if "B" in v.capa and opponent_played_cards != None and opponent_played_cards:
                    id_to_attack = list(opponent_played_cards)[0]
                    actions += str("ATTACK {} {};".format (k, id_to_attack))
                else:
                    actions += str("ATTACK {} -1;".format (k))
        
        # Retry a summoning phase => board was cleared following attack
        sorted_by_value = sorted(my_cards.items(), key=lambda x : x[1].weight)
        
        if nb_played < 6 and me.mana > 0:
            for tupple in sorted_by_value:
                if isinstance(tupple[1], Creature):
                    if tupple[1].mana_cost <= me.mana:
                        actions = actions + str("SUMMON {};".format(tupple[1].id))
                        me.mana -= tupple[1].mana_cost
                        last_summoned = tupple[1].id
        else:
            debug ("Still no room or no mana")
        
        if actions == "":
            actions = "PASS"
        print(actions)
        