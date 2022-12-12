x = 50
y = 50
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = f'{x},{y}'
import pgzrun, random


WIDTH = 800
HEIGHT = 600

ship = Actor('playership1_blue')
ship.x = 370
ship.y = 550

gem = Actor('gemgreen')
gem.x = random.randint(20, 780)
gem.y = 0

score = 0
game_over = False

def init_game():
    global score
    global game_over
    
    game_over = False
    score = 0
    gem.y = 0

def on_mouse_move(pos, rel, buttons):
    ship.x = pos[0]
    if mouse.LEFT in buttons and game_over:
        print(mouse.LEFT)
        init_game()  

def update():
    global score
    global game_over

    if keyboard.left:
        ship.x = ship.x - 5
    if keyboard.right:
        ship.x = ship.x + 5
        
    gem.y = gem.y + 4 + score / 2
    if gem.y > 600:
        game_over = True
    if gem.colliderect(ship):
        gem.x = random.randint(20, 780)
        gem.y = 0
        score = score + 1
      
def draw():
    screen.fill((80,0,70))
    if game_over:
        screen.draw.text('Game Over', (360, 300), color=(255,255,255), fontsize=60)
        screen.draw.text('Final Score: ' + str(score), (360, 350), color=(255,255,255), fontsize=60)
    else:
        gem.draw()
        ship.draw()
        screen.draw.text('Score: ' + str(score), (15,10), color=(255,255,255), fontsize=30)
    
pgzrun.go() # Must be last line