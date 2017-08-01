#############################################################
# boidViewMod.py
# Uses PyGame engine to render swarm of boids.
# by Heiko Nolte / August 2010
# distributed: GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
#############################################################

#Import Modules
from boidSwarmMod import *
import pygame.gfxdraw
import pygame.surface
import pygame.color
from pygame.locals import *
from pygame.color import *
from vector2DMod import *

# Sprite to render a boid
class BoidRender(pygame.sprite.Sprite):
    # Initialize the boid render
    def __init__(self, boid, width=10, height=10, color='blue'):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.color = color
        self.boid = boid
        self.width = width
        self.height = height
        self.image = self.drawBoid()
        self.rect = Rect(self.boid.pos.x, self.boid.pos.y, self.width, self.height)

    # Update boid render position on screen
    def update(self):
        self.rect = Rect(self.boid.pos.x, self.boid.pos.y, self.width, self.height)

    # Draw the boid render on screen
    def drawBoid(self):
        screen = pygame.Surface((self.width, self.height))
        screen.set_colorkey((0,0,0))
        pygame.gfxdraw.filled_circle(screen, self.width/2, self.height/2, self.height/2-1, THECOLORS[self.color])
        return screen

    # Boid render killed
    def kill(self):
        pygame.sprite.Sprite.kill(self)
        print ">>>> removed"

    # Boid render collided
    def collided(self):
        self.kill()
        print ">>>> collided"
        
# Sprite to render a boid
class Target(pygame.sprite.Sprite):
    # Initialize the boid render
    def __init__(self, x=0, y=0, width=10, height=10, color='yellow'):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.x = x
        self.y = y
        self.color = color
        self.width = width
        self.height = height
        self.image = self.drawTarget()
        self.rect = Rect(x, y, self.width, self.height)

    # Update boid render position on screen
    def update(self):
        self.rect = Rect(self.x, self.y, self.width, self.height)

    # Draw the boid render on screen
    def drawTarget(self):
        screen = pygame.Surface((self.width, self.height))
        screen.set_colorkey((0,0,0))
        pygame.gfxdraw.filled_circle(screen, self.width/2, self.height/2, self.height/2-1, THECOLORS[self.color])
        return screen

    # Boid render killed
    def kill(self):
        pygame.sprite.Sprite.kill(self)
        print ">>>> removed"

    # Boid render collided
    def collided(self):
        self.kill()
        print ">>>> collided"        

# Implements the view
class BoidView():
    # Initialize the boid view
    def __init__(self):
        self.winWidth = 800
        self.winHeight = 600
        self.screen = None
        self.prepareView()
        self.doBoidLoop()

    # Initialize the game window
    def initWindow(self,width, height):
        pygame.init()
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Boids V1.0 / by Heiko Nolte')
        pygame.mouse.set_visible(1)
        return screen

    # Create an empty background
    def createEmptySurface(self, screen, rect):
        background = pygame.Surface(rect)
        background = background.convert()
        background.fill((0, 0, 0))
        return background

    # Prepares the boid view
    def prepareView(self):
        # Initialize window
        self.screen = self.initWindow(self.winWidth, self.winHeight)

        # Create swarm of boids
        borders = Rect(25, 25, self.winWidth-25, self.winHeight-25)
        self.boidSwarm = BoidSwarm(borders)

        # Create render objects fot boids in swarm
        self.boidRenderGroup = pygame.sprite.RenderPlain()
        for boid in self.boidSwarm.boids:
            render = BoidRender(boid)
            self.boidRenderGroup.add(render)
            
        # Create target boids have to chase
        self.targetRenderGroup = pygame.sprite.RenderPlain()
        self.target = None
        
        # Create obstacle boids have to avoid
        self.obstacleRenderGroup = pygame.sprite.RenderPlain()
        self.obstacle = None        

        # Create empty background
        self.background = self.createEmptySurface(self.screen, self.screen.get_size())

    # Continuesly renders the boid swarm
    def doBoidLoop(self):
        # Prepary to loop
        clock=pygame.time.Clock()
        doContinue=True

        # Render the boid swarm
        while doContinue:
            clock.tick(20) # fps

            # Catch input event
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                elif event.type == MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()

                    # Set target position
                    if pygame.mouse.get_pressed()[0] == 1:                   
                        if self.target is not None:
                            self.targetRenderGroup.remove(self.target)
                        self.target = Target(pos[0], pos[1])
                        self.boidSwarm.target = Vector2D(pos[0], pos[1])
                        self.targetRenderGroup.add(self.target)
                        
                    # Set obstacle position
                    if pygame.mouse.get_pressed()[2] == 1:                   
                        if self.obstacle is not None:
                            self.obstacleRenderGroup.remove(self.obstacle)
                        self.obstacle = Target(pos[0], pos[1], 10, 10, 'red')
                        self.boidSwarm.obstacle = Vector2D(pos[0], pos[1])

                        self.obstacleRenderGroup.add(self.obstacle)                        

            # Update boids
            self.boidSwarm.updateBoids()
            self.boidRenderGroup.update()
            
            # Update target
            self.targetRenderGroup.update()
            self.obstacleRenderGroup.update()

            # Update screen
            self.screen.blit(self.background, (0,0))
            self.targetRenderGroup.draw(self.screen)
            self.obstacleRenderGroup.draw(self.screen)            
            self.boidRenderGroup.draw(self.screen)
            pygame.display.flip()

# Entrypoint
def main():
    view = BoidView()

    # End game
    pygame.quit()

#this calls the 'main' function when this script is executed
if __name__ == '__main__': main()


