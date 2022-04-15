import pandas as pd
import pygame
import pygame.gfxdraw
import pygame.freetype
import random
import time
import os
import sys
from Button import Button
from Pokemon import Pokemon
from Trainer import Trainer
from Trainer import Potion
from Pokemon import HealthBar


pygame.init()

#POKEDEX
df = pd.read_csv("./assets/pokemon_clean.csv")
N = len(df)

#BUTTON GROUP
button_main = pygame.sprite.Group()
button_fight = pygame.sprite.Group()
button_bag = pygame.sprite.Group()
button_pokemon = pygame.sprite.Group()
button_back = pygame.sprite.Group()

#COLORS
GREEN = (0, 255, 0)
BLUE = (0, 0, 128)
WHITE = (255,255,255)
BLACK = (0,0,0)

#FPS
clock = pygame.time.Clock()
FPS = 60

#SCREEN
PANEL_HEIGHT = 200
WIDTH, HEIGHT = 900, 450 + PANEL_HEIGHT
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pokemon Battle Simulator")

#IMAGES
BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join('bg', 'battle_bg.png')), (900, 450))

#TEXT
font = pygame.font.SysFont('Arial', 40)
font2 = pygame.font.SysFont("Arial", 20)

def draw_bg():
    screen.blit(BACKGROUND,(0,0))

#Draw panel for pokemon information
def draw_bar(screen, x, y, pokemon):    
    pygame.draw.rect(screen, WHITE, pygame.Rect(x,y,250,70))
    pygame.draw.rect(screen, BLACK, pygame.Rect(x,y,250,70), 2)
    screen.blit(font2.render(pokemon.name + " Type: " + pokemon.type1, False, BLACK), (x + 50, y + 10))

#Draw panel for buttons
def draw_panel():
    pygame.draw.rect(screen, WHITE, pygame.Rect(0,HEIGHT-PANEL_HEIGHT,WIDTH,PANEL_HEIGHT))
    pygame.draw.rect(screen, BLACK, pygame.Rect(0,HEIGHT-PANEL_HEIGHT,WIDTH,PANEL_HEIGHT), 2)

#Create button groups filled with single button
def make_buttons(trainer1):
    #Add move number when button clicked
    comm = trainer1.add_move

    #Main button group
    actions = ["FIGHT", "BAG", "POKEMON"]
    for i in range(len(actions)):
        Button(screen, i, button_main, (250 + 300 * (i % 2), 475 + 75 * (int(i / 2) % 2)), actions[i], 40, "black on white", command=comm)

    #Fight button group
    fights = ["Normal Attack", "Special Attack", "Defend", "Special Defend"]
    for i in range(len(fights)):
        Button(screen, i, button_fight, (50 + 300 * (i % 2), 475 + 75 * (int(i / 2) % 2) ), fights[i], 40, "black on white", command=comm)   

    #Bag button group
    for i in range(len(trainer1.potions)):
        Button(screen, i, button_bag, (50 + 300 *(i % 2), 475 + 75 * (int(i / 2) % 2) ), trainer1.potions[i].name, 40, "black on white", command=comm)

    
    #Switch button group
    for i in range(len(trainer1.deck)):
        Button(screen, i, button_pokemon, (125 + 225 * (int(i / 2) % 3), 475 + 75 * (i % 2)), trainer1.deck[i].name, 40, "black on white", command = comm)

    #Back button group
    b_back = Button(screen, 'B', button_back, (850,620), "BACK", 20, "black on white", command = trainer1.reset)    

#Make list of health bars for each pokemon
def make_health_bar(x, y, trainer):
    health_bars = []
    for pokemon in trainer.deck:
        health_bars.append(HealthBar(x, y, pokemon.hp, pokemon.max_hp))
    return health_bars

#Draw buttons depending on current state
def draw_button(trainer1):
    if len(trainer1.movenum) == 0:
        button_main.update()
        button_main.draw(screen)
    elif len(trainer1.movenum) == 1:
        if trainer1.movenum == [0]:
            button_sec = button_fight
        elif trainer1.movenum == [1]:
            button_sec = button_bag
            for i in range(len(trainer1.potions)):
                x = 150 + 350 *(i % 2)
                y = 475 + 75 * (int(i / 2) % 2) 
                screen.blit(font.render(str(trainer1.potions[i].amount), False, BLACK), (x, y))
        elif trainer1.movenum == [2]:
            button_sec = button_pokemon
            
        button_sec.update()
        button_sec.draw(screen)
        if trainer1.deck[trainer1.current].alive:            
            button_back.update()
            button_back.draw(screen)
            
#Create trainer
def create_trainer(name="BOT", bot=False):
    
    #Create pokemon deck
    pokemon_deck = []
    while len(pokemon_deck) < 6:
        n = random.randint(0, N-1)
        pokemon_deck.append(Pokemon(n, bot))

    #Create potions list
    potion_list = [Potion("Small", 50, 3), Potion("Medium", 100, 2), Potion("Mega", 200, 1)]
    
    trainer = Trainer(pokemon_deck, potion_list, name, bot)
    return trainer

def main():
    #Create trainers
    trainer1 = create_trainer("Darel", bot=False)
    trainer2 = create_trainer("AshBot", bot=True)

    #Create game buttons
    make_buttons(trainer1)

    #Create healthbars
    health_bars_1 = make_health_bar(540, 390, trainer1)
    health_bars_2 = make_health_bar(150, 150, trainer2)

    #Game variables
    current_turn = 1
    action_cooldown = 0
    action_wait_time = 60
    just_died = False
    
    run = True
    while run:
        clock.tick(FPS)
        
        trainer1_pokemon = trainer1.deck[trainer1.current]
        trainer2_pokemon = trainer2.deck[trainer2.current]

        #Check if trainer is alive
        trainer1.alive = trainer1.isAlive()
        trainer2.alive = trainer2.isAlive()
            
        #Draw background
        draw_bg()

        #Draw pokemon
        trainer1_pokemon.update(trainer2_pokemon)
        trainer2_pokemon.update(trainer1_pokemon)
        trainer1_pokemon.draw(screen)
        trainer2_pokemon.draw(screen)

        #Draw bar
        draw_bar(screen, 490, 350, trainer1_pokemon)
        draw_bar(screen, 100, 110, trainer2_pokemon)

        #Draw healthbar
        health_bars_1[trainer1.current].draw(screen, trainer1.deck[trainer1.current].hp)
        health_bars_2[trainer2.current].draw(screen, trainer2.deck[trainer2.current].hp)

        #Draw panel
        draw_panel()

        #Draw buttons
        draw_button(trainer1)

        
        if not trainer1.deck[trainer1.current].alive and len(trainer1.movenum) != 2:
            just_died = True
            trainer1.movenum = [2]

        if len(trainer1.movenum) == 2:
            #Check if trainer1's move is valid
            if trainer1.movenum[0] == 1:
                if trainer1.potions[trainer1.movenum[1]].amount <= 0:
                    trainer1.movenum.pop(1)
                    print("Potions are finished")
            elif trainer1.movenum[0] == 2:
                if trainer1.current == trainer1.movenum[1]:
                    trainer1.movenum.pop(1)
                    print("Pokemon is already active")
                elif not trainer1.deck[trainer1.movenum[1]].alive:
                    trainer1.movenum.pop(1)
                    print("Pokemon is deceased")            
        
        if len(trainer1.movenum) == 2 and not just_died:
            # trainer 2 picks move and check if it's valid
            move1 = random.randint(0,2)

            if not trainer2.deck[trainer2.current].alive:
                move1 = 2
                
            if move1 == 0:
                move2 = random.randint(0,3)
                trainer2.movenum = [move1, move2]
            elif move1 == 1:
                move2 = random.randint(0,2)
                if trainer2.potions[move2].amount > 0:
                    trainer2.movenum = [move1, move2]
            elif move1 == 2:
                move2 = random.randint(0,5)
                if trainer2.deck[move2].alive and trainer2.current != move2:
                    trainer2.movenum = [move1, move2]


                        
        #Execute move
        if len(trainer1.movenum) == 2 and len(trainer2.movenum) == 2 and current_turn == 1:               
            action_cooldown += 1
            if action_cooldown >= action_wait_time:
                trainer1.execute_move(trainer2)
                action_cooldown = 0
                current_turn = 2
                just_died = False

        elif len(trainer1.movenum) == 2 and just_died:
            action_cooldown += 1
            if action_cooldown >= action_wait_time:
                trainer1.execute_move(trainer2)
                action_cooldown = 0
                just_died = False

        if not trainer2.deck[trainer2.current].alive:
            trainer2.movenum = []
            move2 = random.randint(0,5)
            if trainer2.deck[move2].alive and trainer2.current != move2:
                trainer2.movenum = [2, move2]            
            
        if len(trainer2.movenum) == 2 and current_turn == 2:
            action_cooldown += 1
            if action_cooldown >= action_wait_time:
                trainer2.execute_move(trainer1)
                current_turn = 1
                action_cooldown = 0
                
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                    run = False

        #End the game if one of the trainer is not alive
        if not trainer1.alive:
            screen.blit(font.render("YOU LOSE", False, BLACK), (WIDTH / 2 - 100, HEIGHT / 2 - 50))
            print("you win")
            pygame.quit()
            sys.exit()
            run = False
        if not trainer2.alive:
            screen.blit(font.render("YOU WIN", False, BLACK), (WIDTH / 2 - 100, HEIGHT / 2 - 50))
            print("you lose")
            pygame.quit()
            sys.exit()
            run = False
            
        pygame.display.update()

if __name__ == "__main__":
    main()
