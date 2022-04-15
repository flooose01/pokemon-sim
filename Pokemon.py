import pandas as pd
import pygame
import os

#POKEMON CSV
df = pd.read_csv('./assets/pokemon_clean.csv')

#COLORS
GREEN = (0, 255, 0)
RED = (255, 0, 0)

class HealthBar():
    def __init__(self, x, y, hp, max_hp):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp
        
    def draw(self, screen, hp):
	#Update with new health
        self.hp = hp
	#Calculate health ratio
        ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, RED, (self.x, self.y, 180, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 180 * ratio, 20))

class Pokemon:
    def __init__(self, pokedex_id, bot, level=100):
        self.level = level
        self.name = df.loc[pokedex_id]['Name']
        self.max_hp = df.loc[pokedex_id]['HP'] * 3 * level / 100
        self.hp = self.max_hp
        self.attack = df.loc[pokedex_id]['Attack'] * level / 100
        self.defense = df.loc[pokedex_id]['Defense'] * level / 100
        self.spattack = df.loc[pokedex_id]['Sp. Atk'] * level / 100
        self.spdefense = df.loc[pokedex_id]['Sp. Def'] * level / 100
        self.speed = df.loc[pokedex_id]['Speed'] * level / 100
        self.type1 = df.loc[pokedex_id]['Type 1']
        self.alive = True
        self.spblock = False
        self.action = [3, 0] #30 IDLE #00 ATTACK #01 SPATT #02 DEF ...
        self.animation_list = [[self.animate_att, self.animate_spatt, self.animate_def, self.animate_spdef], #Fight Animation
                               [self.idle, self.idle, self.idle], #Potions Animation
                               [self.idle, self.idle, self.idle, self.idle, self.idle, self.idle], #Switching animation
                               [self.idle]] #Idle animation
        self.moves = [self.att, self.spatt, self.defend, self.spdef] #Moves
        self.frame_index = 0
        self.bot = bot

        #POSITION
        if not bot:
            self.x, self.y = 240, 360
            back_pic = pygame.image.load(os.path.join('back', str(pokedex_id+1) + '.png'))
            self.image = pygame.transform.scale(back_pic, (400,400))
        else:
            self.x, self.y = 650, 200
            front_pic = pygame.image.load(os.path.join('front', str(pokedex_id+1)+'.png'))
            self.image = pygame.transform.scale(front_pic, (300,300))

        self.rect = self.image.get_rect()
        

    def __repr__(self):
        return f"This level {self.level} {self.name} has {self.hp} hit points remaining. It is a {self.type1} type Pokemon"

    def knock_out(self):
        self.alive = False
        self.hp = 0
        self.name = self.name + " X"
        print(f"{self.name} is knocked out!")

    def lose_hp(self, damage):
        self.hp -= damage
        print("{name} is damaged by {damage}HP".
              format(name=self.name, damage=damage))
        if self.hp <= 0:
            self.knock_out()

    def gain_hp(self, amount):
        if self.hp + amount > self.max_hp:
            amount = self.max_hp - self.hp
            self.hp = self.max_hp
        else:
            self.hp += amount
            
        print("{name} gain {amount}HP".format(name=self.name,
                                              amount=amount))

    def gain_def(self, amount):
        self.defense += amount
        print(f"{self.name}'s defense rose")

    def lose_def(self, amount):
        self.defense -= amount
        print(f"{self.name}'s defense decrease")

    #Might implement in the future
    def gain_att(self, amount):
        self.attack += amount
        print(f"{self.name}'s attack rose")

    def lose_att(self, amount):
        self.attack -= amount
        print(f"{self.name}'s attack decrease")

    #Execute move
    def move(self, skill_number, opponent):
        self.moves[skill_number](opponent)

    #MOVES
      
    def att(self, opponent):
        print(f"{self.name} uses Normal Attack")

        damage = self.attack - opponent.defense / 4
        if damage < 10:
            damage = 10

        opponent.lose_hp(damage)

    def spatt(self, opponent):
        print(f"{self.name} uses Special Attack")

        damage = self.spattack - opponent.spdefense / 4
        if damage < 10:
            damage = 10

        if opponent.spblock:
            print(f"{opponent.name} blocked the attack")

        else:
            k = self.effective(opponent)
            if k < 1:
                print("It's not very effective...")
            elif k > 1:
                print("It's super effective!")

            opponent.lose_hp(damage * k)

    def defend(self, opponent):
        print(f"{self.name} uses Defense")
        self.gain_def(0.25 * self.defense)

    def spdef(self, opponent):
        print(f"{self.name} uses Special Defense")
        self.spblock = True

    #ANIMATIONS
           
    def draw(self, screen):
        self.rect.center = (self.x, self.y)
        screen.blit(self.image, self.rect)
        
    def update(self, opponent):
        frame = 30
        self.animation_list[self.action[0]][self.action[1]](opponent, frame)

        if self.frame_index >= frame:
            self.idle(opponent, frame)

    def idle(self, opponent, frame):
        self.action = [3, 0]
        self.frame_index = 0
        
    def animate_att(self, opponent, frame):
        self.frame_index += 1
        if self.bot:
            value = -100
        else:
            value = 100
        
        if self.frame_index <= frame / 2:
            self.x += value / (frame / 2)
        else:
            self.x -= value / (frame / 2)

    def animate_spatt(self, opponent, frame):
        self.frame_index += 1
        if self.bot:
            value = -300
        else:
            value = 300
        
        if self.frame_index <= frame / 2:
            self.x += value / (frame / 2)
        else:
            self.x -= value / (frame / 2)

    def animate_def(self, opponent, frame):
        self.frame_index += 1
        if self.frame_index <= 7:
            self.y += 100 / (frame / 4)
        elif self.frame_index <= 14:
            self.y -= 100 / (frame / 4)
        elif self.frame_index <= 22:
            self.y += 100 / (frame / 4)
        else:
            self.y -= 100 / (frame / 4)
            
    def animate_spdef(self, opponent, frame):
        self.frame_index += 1
        if self.frame_index <= 7:
            self.y -= 100 / (frame / 4)
        elif self.frame_index <= 14:
            self.y += 100 / (frame / 4)
        elif self.frame_index <= 22:
            self.y -= 100 / (frame / 4)
        else:
            self.y += 100 / (frame / 4)


    #List of effectiveness according to elements
    def effective(self, opponent):

        # WEAKNESS        
        if self.type1 == 'Normal' and \
                (opponent.type1 == 'Rock' or
                 opponent.type1 == 'Ghost' or
                 opponent.type1 == 'Steel'):
            return 0.5
        elif self.type1 == 'Fighting' and \
                (opponent.type1 == 'Flying' or
                 opponent.type1 == 'Poison' or
                 opponent.type1 == 'Psychic' or
                 opponent.type1 == 'Bug' or
                 opponent.type1 == 'Ghost'):
            return 0.5
        elif self.type1 == 'Flying' and \
                (opponent.type1 == 'Rock' or
                 opponent.type1 == 'Steel' or
                 opponent.type1 == 'Electric'):
            return 0.5
        elif self.type1 == 'Poison' and \
                (opponent.type1 == 'Ground' or
                 opponent.type1 == 'Poison' or
                 opponent.type1 == 'Rock' or
                 opponent.type1 == 'Steel' or
                 opponent.type1 == 'Ghost'):
            return 0.5
        elif self.type1 == 'Ground' and \
                (opponent.type1 == 'Flying' or
                 opponent.type1 == 'Grass' or
                 opponent.type1 == 'Bug'):
            return 0.5
        elif self.type1 == 'Rock' and \
                (opponent.type1 == 'Fighting' or
                 opponent.type1 == 'Ground' or
                 opponent.type1 == 'Steel'):
            return 0.5
        elif self.type1 == 'Bug' and \
                (opponent.type1 == 'Fighting' or
                 opponent.type1 == 'Flying' or
                 opponent.type1 == 'Ghost' or
                 opponent.type1 == 'Steel' or
                 opponent.type1 == 'Fire'):
            return 0.5
        elif self.type1 == 'Ghost' and \
                (opponent.type1 == 'Normal' or
                 opponent.type1 == 'Dark'):
            return 0.5
        elif self.type1 == 'Steel' and \
                (opponent.type1 == 'Steel' or
                 opponent.type1 == 'Fire' or
                 opponent.type1 == 'Water' or
                 opponent.type1 == 'Electric'):
            return 0.5
        elif self.type1 == 'Fire' and \
                (opponent.type1 == 'Rock' or
                 opponent.type1 == 'Fire' or
                 opponent.type1 == 'Water' or
                 opponent.type1 == 'Dragon'):
            return 0.5
        elif self.type1 == 'Water' and \
                (opponent.type1 == 'Water' or
                 opponent.type1 == 'Grass' or
                 opponent.type1 == 'Dragon'):
            return 0.5
        elif self.type1 == 'Grass' and \
                (opponent.type1 == 'Fire' or
                 opponent.type1 == 'Flying' or
                 opponent.type1 == 'Poison' or
                 opponent.type1 == 'Bug' or
                 opponent.type1 == 'Dragon' or
                 opponent.type1 == 'Steel' or
                 opponent.type1 == 'Grass'):
            return 0.5
        elif self.type1 == 'Electric' and \
                (opponent.type1 == 'Ground' or
                 opponent.type1 == 'Grass' or
                 opponent.type1 == 'Dragon' or
                 opponent.type1 == 'Electric'):
            return 0.5
        elif self.type1 == 'Psychic' and \
                (opponent.type1 == 'Steel' or
                 opponent.type1 == 'Psychic' or
                 opponent.type1 == 'Dark'):
            return 0.5
        elif self.type1 == 'Ice' and \
                (opponent.type1 == 'Steel' or
                 opponent.type1 == 'Fire' or
                 opponent.type1 == 'Water' or
                 opponent.type1 == 'Ice'):
            return 0.5
        elif self.type1 == 'Dragon' and \
                (opponent.type1 == 'Steel'):
            return 0.5
        elif self.type1 == 'Dark' and \
                (opponent.type1 == 'Fighting' or
                 opponent.type1 == 'Dark'):
            return 0.5

        # STRENGTH
        elif self.type1 == 'Fighting' and \
                (opponent.type1 == 'Normal' or
                 opponent.type1 == 'Rock' or
                 opponent.type1 == 'Steel' or
                 opponent.type1 == 'Ice' or
                 opponent.type1 == 'Dark'):
            return 2
        elif self.type1 == 'Flying' and \
                (opponent.type1 == 'Fighting' or
                 opponent.type1 == 'Bug' or
                 opponent.type1 == 'Grass'):
            return 2
        elif self.type1 == 'Poison' and \
                (opponent.type1 == 'Grass'):
            return 2
        elif self.type1 == 'Ground' and \
                (opponent.type1 == 'Poison' or
                 opponent.type1 == 'Rock' or
                 opponent.type1 == 'Steel' or
                 opponent.type1 == 'Fire' or
                 opponent.type1 == 'Electric'):
            return 2
        elif self.type1 == 'Rock' and \
                (opponent.type1 == 'Flying' or
                 opponent.type1 == 'Bug' or
                 opponent.type1 == 'Fire' or
                 opponent.type1 == 'Ice'):
            return 2
        elif self.type1 == 'Bug' and \
                (opponent.type1 == 'Grass' or
                 opponent.type1 == 'Psychic' or
                 opponent.type1 == 'Dark'):
            return 2
        elif self.type1 == 'Ghost' and \
                (opponent.type1 == 'Ghost' or
                 opponent.type1 == 'Psychic'):
            return 2
        elif self.type1 == 'Steel' and \
                (opponent.type1 == 'Rock' or
                 opponent.type1 == 'Ice'):
            return 2
        elif self.type1 == 'Fire' and \
                (opponent.type1 == 'Bug' or
                 opponent.type1 == 'Steel' or
                 opponent.type1 == 'Grass' or
                 opponent.type1 == 'Ice'):
            return 2
        elif self.type1 == 'Grass' and \
                (opponent.type1 == 'Ground' or
                 opponent.type1 == 'Rock' or
                 opponent.type1 == 'Water'):
            return 2
        elif self.type1 == 'Water' and \
                (opponent.type1 == 'Ground' or
                 opponent.type1 == 'Rock' or
                 opponent.type1 == 'Fire'):
            return 2
        elif self.type1 == 'Electric' and \
                (opponent.type1 == 'Flying' or
                 opponent.type1 == 'Water'):
            return 2
        elif self.type1 == 'Psychic' and \
                (opponent.type1 == 'Fighting' or
                 opponent.type1 == 'Poison'):
            return 2
        elif self.type1 == 'Ice' and \
                (opponent.type1 == 'Ground' or
                 opponent.type1 == 'Flying' or
                 opponent.type1 == 'Grass' or
                 opponent.type1 == 'Dragon'):
            return 2
        elif self.type1 == 'Dragon' and \
                (opponent.type1 == 'Dragon'):
            return 2
        elif self.type1 == 'Dark' and \
                (opponent.type1 == 'Ghost' or
                 opponent.type1 == 'Psychic'):
            return 2

        # Normal Sp. Attack
        else:
            return 1

