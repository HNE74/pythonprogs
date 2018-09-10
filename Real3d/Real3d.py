#Import Modules
import os, pygame
import pygame.surface
import pygame.color
from pygame.locals import *
from pygame.color import *;

class GroundLine():
    
    def __init__(self, ypos, width, zpos, sCalc):
        self.ypos = ypos
        self.width = width
        self.zpos = zpos
        self.sCalc = sCalc
        
    def draw(self, background, color):    
        leftPos = self.sCalc.toScreenCoordinates([-self.width / 2, self.ypos, self.zpos]) 
        rightPos = self.sCalc.toScreenCoordinates([self.width, self.ypos, self.zpos])
        
        pygame.draw.line(background, THECOLORS[color], leftPos, rightPos, 1) 
        
    def update(self, zdif):
        self.zpos = self.zpos - zdif
        if self.zpos <= -1000:
            self.zpos = 1000        
        

# Rectangle
class Carre():
    
    def __init__(self, xpos, ypos, width, height, zpos, sCalc):
        self.xpos = xpos
        self.ypos = ypos
        self.width = width
        self.height = height
        self.zpos = zpos 
        self.sCalc = sCalc       
        
    def draw(self, background, color): 
        
        topLeftX = self.xpos - self.width / 2
        topLeftY = self.ypos - self.height / 2
        topRightX = self.xpos + self.width / 2
        topRightY = self.ypos - self.height / 2

        bottomLeftX = self.xpos - self.width / 2
        bottomLeftY = self.ypos + self.height / 2        
        bottomRightX = self.xpos + self.width / 2
        bottomRightY = self.ypos + self.height / 2
        
        topLeftScreen = self.sCalc.toScreenCoordinates([topLeftX, topLeftY, self.zpos])
        topRightScreen = self.sCalc.toScreenCoordinates([topRightX, topRightY, self.zpos])        
        bottomLeftScreen = self.sCalc.toScreenCoordinates([bottomLeftX, bottomLeftY, self.zpos])
        bottomRightScreen = self.sCalc.toScreenCoordinates([bottomRightX, bottomRightY, self.zpos])         
        
        pygame.draw.polygon(background, THECOLORS[color], [topLeftScreen, topRightScreen, \
                                                           bottomRightScreen, bottomLeftScreen] )
    
    def update(self, zdif):
        self.zpos = self.zpos - zdif
        if self.zpos <= -1000:
            self.zpos = 1000
            
class ScreenCalculator():
    
    def __init__(self, eye):
        self.eye = eye
        
    """ 
    ----------------------------------------   
    Formula to solve Sx  
    ----------------------------------------  
    Ez = distance from eye to the center of the screen 
    Ex = X coordinate of the eye  
    Px = X coordinate of the 3D point  
    Pz = Z coordinate of the 3D point  
    
               Ez*(Px-Ex)  
    Sx  = -----------------------  + Ex   
                  Ez+Pz   
                  
    ----------------------------------------   
    Formula to solve Sy  
    ----------------------------------------  
    Ez = distance from eye to the center of the screen 
    Ey = Y coordinate of the eye   
    Py = Y coordinate of the 3D point  
    Pz = Z coordinate of the 3D point      

              Ez*(Py-Ey)  
    Sy  = -------------------  + Ey        
                 Ez+Pz 
    """   
    def toScreenCoordinates(self, point):
        
        #S.x = (eye.z * (P.x-eye.x)) / (eye.z + P.z) + eye.x;
        x = (self.eye[2] * (point[0] - self.eye[0])) / (self.eye[2] + point[2]) + self.eye[0]
        
        #S.y = (eye.z * (P.y-eye.y)) / (eye.z + P.z) + eye.y;
        y = (self.eye[2] * (point[1] - self.eye[1])) / (self.eye[2] + point[2]) + self.eye[1]
        
        return [x,y]       
    
    
        
        
def main():
    """this function is called when the program starts.
       it initializes everything it needs, then runs in
       a loop until the function returns."""
   
    # Initialize Everything
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Real 3D')
    pygame.mouse.set_visible(1)

    # Rectangle to be shown
    calc = ScreenCalculator([400, 300, 1000])
    carre1 = Carre(500, 310, 40, 40, 1000, calc)
    carre2 = Carre(300, 310, 40, 40, 1000, calc)
    carre3 = Carre(400, 285, 40, 40, 1000, calc)    
    carre4 = Carre(350, 305, 40, 40, 1000, calc)   
    carre5 = Carre(410, 295, 10, 10, 1000, calc)  
    
    calc2 = ScreenCalculator([400, 290, 1000])
    ground = []
    anz = 20
    for ndx in range(anz): 
        line = GroundLine(300, 2000, 1000 - (2000 / anz * ndx), calc2)
        ground.append(line)

    # Main Loop
    clock=pygame.time.Clock()
    
    while 1:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT:
                return
            
        # Create empty background
        background = pygame.Surface(screen.get_size())
        background = background.convert()
        background.fill((0, 0, 0))             
       
        # Draw ground lines
        for ndx in range(len(ground)): 
            ground[ndx].draw(background, 'green')   
               
        # Draw rectangles
        carre1.draw(background, 'blue')
        carre2.draw(background, 'yellow')
        carre3.draw(background, 'red')
        carre4.draw(background, 'cyan')  
        carre5.draw(background, 'white')  
           
        # Move rectangles
        carre1.update(10)
        carre2.update(50)
        carre3.update(5)
        carre4.update(20)
        carre5.update(2)  
        
        # Move ground lines
        for ndx in range(len(ground)): 
            ground[ndx].update(2)
                      
        #Draw Everything
        screen.blit(background, (0, 0))
        pygame.display.flip()
               
#this calls the 'main' function when this script is executed
if __name__ == '__main__': main()
