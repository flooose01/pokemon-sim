import random
from Pokemon import Pokemon

class Potion:
    def __init__(self, name, hp, amount):
        self.name = name
        self.hp = hp
        self.amount = amount

class Trainer:
    def __init__(self, pokemon_list, potion_list, name="BOT", bot=False):
        self.name = name
        self.deck = pokemon_list
        self.potions = potion_list
        self.current = 0        
        self.movenum = []
        self.bot = bot
        self.alive = True

    def __repr__(self):
        print("The trainer {name} has the following pokemon".
              format(name=self.name))
        for pokemon in self.deck:
            print(pokemon)
        return "The current active pokemon is {name}". \
            format(name=self.deck[self.current].name)

    #Check if trainer is alive
    def isAlive(self):
        for pokemon in self.deck:
            if pokemon.alive:
                return True

        return False

    #Add move to current state
    def add_move(self, value):
        self.movenum.append(value)

    #Reset state    
    def reset(self, value='B'):
        self.movenum = []

    #Execute move    
    def execute_move(self, opponent):
        my_pokemon = self.deck[self.current]
        op_pokemon = opponent.deck[opponent.current]

        if self.movenum[0] == 0:
            my_pokemon.move(self.movenum[1], op_pokemon)
        elif self.movenum[0] == 1:
            self.use_potion(self.movenum[1])
        elif self.movenum[0] == 2:
            self.switch(self.movenum[1])
            
        my_pokemon.action = [self.movenum[0], self.movenum[1]]
        self.reset()
        my_pokemon.spblock = False

    #Use potion
    def use_potion(self, potion_index):
        self.potions[potion_index].amount -= 1
        print(self.name + " uses " + self.potions[potion_index].name + " potion")
        self.deck[self.current].gain_hp(self.potions[potion_index].hp)

    #Switch pokemon
    def switch(self, switch_index):
        print("Switched to "  + self.deck[switch_index].name)
        self.current = switch_index
