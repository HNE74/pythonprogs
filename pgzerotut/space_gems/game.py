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

def update():
    global score

    if keyboard.left:
        ship.x = ship.x - 5
    if keyboard.right:
        ship.x = ship.x + 5
        
    gem.y = gem.y + 4
    if gem.y > 600:
        gem.x = random.randint(20, 780)
        gem.y = 0
    if gem.colliderect(ship):
        gem.x = random.randint(20, 780)
        gem.y = 0
        score = score + 1
      
def draw():
    screen.fill((80,0,70))
    screen.draw.text('Score: ' + str(score), (15,10), color=(255,255,255), fontsize=30)
    gem.draw()
    ship.draw()
    
pgzrun.go() # Must be last line