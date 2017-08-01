##########################################################
### Hungry Hamster V1.0
### by Heiko Nolte / March 2010
### Pac Man like game where the player, impersoned by a hamster,
### is chased by snakes. Applies the theseus maze ### generation
### algorithm.
### This code is distributed under
### GNU GENERAL PUBLIC LICENSE, Version 3.
##########################################################

import sys, os, pygame, random, datetime
from pygame import time
from pygame.locals import *
from pygame.color import *
from pygame.gfxdraw import *

# N,S,E,W Vectors
toCheckX = [-1, 0, 1, 0]
toCheckY = [0, -1, 0, 1]

# Pygame window dimensions
screenWidth=800
screenHeight=600

# Manages images and sound resources
class ResourceManager:

    # Initialize resource manager
    def __init__(self, path):
        self.path = path

        # Frame images for animated sprites
        self.hamsterLeftFrames = []
        self.hamsterRightFrames = []
        self.snakeLeftFrames = []
        self.snakeRightFrames = []

        # Load sounds and images
        self.loadImages()
        self.loadSounds()

    # load image
    def loadImage(self, name, colorkey=None):
        fullname = self.path + '/' + name
        try:
            image = pygame.image.load(fullname)
        except pygame.error, message:
            print 'Cannot load image:', fullname
            raise SystemExit, message
        image = image.convert()
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, RLEACCEL)
        return image, image.get_rect()

    # preload images
    def loadImages(self):
        # Hamster
        self.hamsterLeftFrames.append(self.loadImage('hamster_left1.PNG', (0,0,0)))
        self.hamsterLeftFrames.append(self.loadImage('hamster_left2.PNG', (0,0,0)))
        self.hamsterRightFrames.append(self.loadImage('hamster_right1.PNG', (0,0,0)))
        self.hamsterRightFrames.append(self.loadImage('hamster_right2.PNG', (0,0,0)))

        # Snake
        self.snakeLeftFrames.append(self.loadImage('snake_left1.JPG', (0,0,0)))
        self.snakeLeftFrames.append(self.loadImage('snake_left2.JPG', (0,0,0)))
        self.snakeRightFrames.append(self.loadImage('snake_right1.JPG', (0,0,0)))
        self.snakeRightFrames.append(self.loadImage('snake_right2.JPG', (0,0,0)))

    # load sound
    def loadSound(self, name):
        class NoneSound:
            def play(self): pass
        if not pygame.mixer or not pygame.mixer.get_init():
            return NoneSound()
        fullname = self.path + '/' + name
        try:
            sound = pygame.mixer.Sound(fullname)
        except pygame.error, message:
            print 'Cannot load sound:', fullname
            raise SystemExit, message
        return sound

    # preload sounds
    def loadSounds(self):
        pass

# Generates a maze and provides a method to fetch
# the shortest path between two locations within the maze
class Maze():

    # Initialize state data instance
    def __init__(self, width=10, height=10, xpos=1, ypos=1):
        self.height = height
        self.width = width
        self.xpos = xpos
        self.ypos = ypos
        self.minFound = 10000

    # Clone the current maze
    def cloneMaze(self):
        cloned = []
        for y in range(self.height):
            line = []
            sourceLine = self.maze[y]
            cloned.append(line)
            for x in range(self.width):
                value = sourceLine[x]
                line.append(value)

        return cloned

    # Print maze to console for test purposes
    def printMaze(self, toPrint=None):
        # Use current or passed maze
        cnt=0
        if toPrint != None:
            maze = toPrint
        else:
            maze = self.maze

        # Iterate over maze tiles and print to console
        for y in range(self.height):
            line = maze[y]
            output = ''
            for x in range(self.width):
                if line[x] == 0:
                    output = output + ' '
                elif line[x] == 2:
                    output = output + 'O'
                    cnt = cnt + 1
                elif line[x] > 9:
                    output = output + str(line[x] % 10)
                else:
                    output = output + '#'
            print output

    # Print maze to console for test purposes
    def printMazeWithPath(self, path, toPrint=None):
        # Use current or passed maze
        if toPrint != None:
            maze = toPrint
        else:
            maze = self.maze

        # Iterate over maze tiles and print to console
        for y in range(self.height):
            line = maze[y]
            output = ''
            for x in range(self.width):
                if line[x] != 1:
                    # Check if position in path
                    isPath = False
                    for ndx in range(len(path)):
                        coord = path[ndx]
                        xc = coord[0]
                        yc = coord[1]
                        if xc == x and yc == y:
                            output = output + 'O'
                            isPath = True
                    if not isPath:
                        output = output + ' '
                elif line[x] == 1:
                    output = output + '#'
                else:
                    output = output + ' '
            print output

    # Generates fixed maze to test pathfind algorithm
    def generateTestMaze(self):
        self.maze = []
        line = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        self.maze.append(line)
        line = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        self.maze.append(line)
        line = [1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1]
        self.maze.append(line)
        line = [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1]
        self.maze.append(line)
        line = [1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1]
        self.maze.append(line)
        line = [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1]
        self.maze.append(line)
        line = [1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1]
        self.maze.append(line)
        line = [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1]
        self.maze.append(line)
        line = [1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1]
        self.maze.append(line)
        line = [1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1]
        self.maze.append(line)
        line = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        self.maze.append(line)

    # Finds the shortest way between 2 points in maze
    # using the Lee algorithm
    def findWay(self, xstart, ystart, xend, yend):
        cMaze = self.cloneMaze()
        self.fetchPathToTarget(xstart, ystart, xend, yend, 10, cMaze)
        path = []
        self.backtrackPath(xend, yend, xstart, ystart, cMaze, path)
        return path

    # Returns a list of tiles representing the path from the
    # start tile to the target tile
    def backtrackPath(self, xpos, ypos, xstart, ystart, maze, path):
        # N,S,E,W directions
        global toCheckX
        global toCheckY

        # path list
        path.append([xpos, ypos])

        # Generate list until start position reached
        while(xpos != xstart or ypos != ystart):
            # Fetch value of the current tile
            currentTile = self.fetchTile(xpos, ypos, maze)

            # Find tile with next smaller value
            for ndx in range(len(toCheckX)):
                checkTile = self.fetchTile(xpos+toCheckX[ndx], ypos+toCheckY[ndx], maze)

                # Continue check if no wall tile
                if checkTile < currentTile and checkTile > 9:
                    xpos = xpos + toCheckX[ndx]
                    ypos = ypos + toCheckY[ndx]

                    # Return list if target reached
                    if xpos == xstart and ypos == ystart:
                        path.append([xpos, ypos])
                        path.reverse()
                        return
                    else:
                        # Add tile to path and continue search
                        path.append([xpos, ypos])
                        break

    # Fetches path having optimal length to target
    def fetchPathToTarget(self, xpos, ypos, xend, yend, cnt, maze):
        # Vectors to check adjacent tiles
        global toCheckX
        global toCheckY

        # Initialize tile list
        tileList = []
        tileList.append([xpos, ypos])
        self.setTile(xpos, ypos, cnt, maze)
        cnt = cnt + 1

        # Continue while target not reached
        searchPath = True
        while(searchPath):
            cnt = cnt + 1
            nextTileList = []
            for cndx in range(len(tileList)):
                xc = tileList[cndx][0]
                yc = tileList[cndx][1]

                # Abort while loop if target reached
                if xc == xend and yc == yend:
                    searchPath = False
                    break

                # Check n,s,e,w tile if empty
                for ndx in range(len(toCheckX)):
                    xcheck = xc + toCheckX[ndx]
                    ycheck = yc + toCheckY[ndx]

                    # Set cnt value on check tile if empty
                    # and add it to tile list for next iteration
                    tile = self.fetchTile(xcheck, ycheck, maze)
                    if tile == 0:
                        self.setTile(xcheck, ycheck, cnt, maze)
                        nextTileList.append([xcheck, ycheck])

            # Update tile list
            tileList = nextTileList

    # Fetch tile on coordinate position
    def fetchTile(self, xpos, ypos, maze=None):
        if maze == None:
            maze = self.maze
        line = maze[ypos]
        tile = line[xpos]
        return tile

    # Set tile on coordinate position
    def setTile(self, xpos, ypos, value, maze=None):
        if maze == None:
            maze = self.maze
        line = maze[ypos]
        line[xpos] = value

    # Randomly generate maze
    def generateMaze(self, xstart, ystart, gaps):
        # Create maze without corridors
        self.maze=[]
        for y in range(self.height):
            line = []
            self.maze.append(line)
            for x in range(self.width):
                line.append(1)

        self.generateCorridor(xstart, ystart)
        self.generateGaps(gaps)

    # Randomly add gaps to walls
    def generateGaps(self, gaps):
        # N,S,E,W Vectors
        global toCheckX
        global toCheckY

        # Create list of tiles which could become gaps
        tiles = []
        for y in range(self.height-2):
            for x in range(self.width-2):
                if self.fetchTile(x+1 + toCheckX[0], y+1 + toCheckY[0]) == 1 and \
                   self.fetchTile(x+1 + toCheckX[2], y+1 + toCheckY[2]) == 1 and \
                   self.fetchTile(x+1 + toCheckX[1], y+1 + toCheckY[1]) == 0 and \
                   self.fetchTile(x+1 + toCheckX[3], y+1 + toCheckY[3]) == 0:
                       tiles.append([x+1, y+1])
                elif self.fetchTile(x+1 + toCheckX[0], y+1 + toCheckY[0]) == 0 and \
                   self.fetchTile(x+1 + toCheckX[2], y+1 + toCheckY[2]) == 0 and \
                   self.fetchTile(x+1 + toCheckX[1], y+1 + toCheckY[1]) == 1 and \
                   self.fetchTile(x+1 + toCheckX[3], y+1 + toCheckY[3]) == 1:
                       tiles.append([x+1, y+1])

        # Place gaps randomly
        cnt = 0
        exitCnt = 0
        while(cnt < gaps and len(tiles) > 0):
            ndx = random.randint(0, len(tiles)-1)
            if (self.fetchTile(tiles[ndx][0] + toCheckX[0], tiles[ndx][1] + toCheckY[0]) == 1 and \
               self.fetchTile(tiles[ndx][0] + toCheckX[2], tiles[ndx][1] + toCheckY[2]) == 1 and \
               self.fetchTile(tiles[ndx][0] + toCheckX[1], tiles[ndx][1] + toCheckY[1]) == 0 and \
               self.fetchTile(tiles[ndx][0] + toCheckX[3], tiles[ndx][1] + toCheckY[3]) == 0) or \
               (self.fetchTile(tiles[ndx][0] + toCheckX[0], tiles[ndx][1] + toCheckY[0]) == 0 and \
               self.fetchTile(tiles[ndx][0] + toCheckX[2], tiles[ndx][1] + toCheckY[2]) == 0 and \
               self.fetchTile(tiles[ndx][0] + toCheckX[1], tiles[ndx][1] + toCheckY[1]) == 1 and \
               self.fetchTile(tiles[ndx][0] + toCheckX[3], tiles[ndx][1] + toCheckY[3]) == 1):
                    # Set gap
                    self.setTile(tiles[ndx][0], tiles[ndx][1], 0)
                    tiles.remove(tiles[ndx])
                    cnt = cnt + 1
            else:
                # Emergency exit ;-)
                exitCnt = exitCnt + 1
                if exitCnt == 100:
                    break

    # Creates a dictoinary with environment descriptions for each tile
    # in the maze. The keys are strings having the format x,y
    def fetchEnvDescriptions(self):
        toCheck = [(0,-1), (-1,0), (1,0), (0,1)]

        result = {} # Dict where tile environment can be fetched from
        for y in range(self.height):
            for x in range(self.width):
                # Init key and environment descriptor
                key = str(x) + "," + str(y)
                desc = ""
                for ndx in range(len(toCheck)):
                    # Add digit to descriptor
                    xc = x + toCheck[ndx][0]
                    yc = y + toCheck[ndx][1]
                    if xc < 0 or xc >= self.width or \
                       yc < 0 or yc >= self.height:
                           desc = desc + "0"
                    else:
                        tile = self.fetchTile(xc, yc)
                        desc = desc + str(tile)
                # Add descriptor to dict
                result[key] = desc
                print desc
        return result

    # Generate corridors recusively
    def generateCorridor(self, xpos, ypos):
        # N,S,E,W Vectors
        toCheckX = [-1, 0, 1, 0]
        toCheckY = [0, -1, 0, 1]

        # Iterate until all directions checked
        while(len(toCheckX) > 0):
            # Determine tile to check
            ndx = random.randint(0, len(toCheckX)-1)
            xnew = xpos + toCheckX[ndx] * 2
            ynew = ypos + toCheckY[ndx] * 2

            # Avoid to exceed maze borders
            if xnew < 1 or xnew > self.width-1 or \
               ynew < 1 or ynew > self.height-1:
                toCheckX.pop(ndx)
                toCheckY.pop(ndx)
                continue

            # Check if tile is still solid
            checkTile=self.fetchTile(xnew, ynew)
            if checkTile == 1:
                self.setTile(xpos + toCheckX[ndx], ypos + toCheckY[ndx], 0)
                self.setTile(xnew, ynew, 0)
                self.generateCorridor(xnew, ynew)

            # Remove direction from list
            toCheckX.pop(ndx)
            toCheckY.pop(ndx)

# Sprite representing a maze tile
class MazeTile(pygame.sprite.Sprite):

    # Initialize background tile
    def __init__(self, tiledim, type, color):
        pygame.sprite.Sprite.__init__(self)
        self.rect = tiledim
        self.width = tiledim.width
        self.height = tiledim.height
        self.type = type
        self.color = color

        self.w1_4 = round(self.rect.width / 4 * 1)
        self.w2_4 = round(self.rect.width / 4 * 2)
        self.w3_4 = round(self.rect.width / 4 * 3)
        self.h1_4 = round(self.rect.height / 4 * 1)
        self.h2_4 = round(self.rect.height / 4 * 2)
        self.h3_4 = round(self.rect.height / 4 * 3)
        self.radius = self.w1_4 / 2.5
        self.createTileImage()
        self.image.set_colorkey((0,0,0), RLEACCEL)

    # Create an empty background tile
    def createEmptyTileImage(self):
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.image = self.image.convert()
        self.image.fill(THECOLORS['black'])

     # Creates a tile image according to its type
    def createTileImage(self):
        self.createEmptyTileImage()

        if self.type == 0:
            self.imageType0()
        elif self.type == 1:
            self.imageType1()
        elif self.type == 2:
            self.imageType2()
        elif self.type == 3:
            self.imageType3()
        elif self.type == 4:
            self.imageType4()
        elif self.type == 5:
            self.imageType5()
        elif self.type == 6:
            self.imageType6()
        elif self.type == 7:
            self.imageType7()
        elif self.type == 8:
            self.imageType8()
        elif self.type == 9:
            self.imageType9()
        elif self.type == 10:
            self.imageType10()
        elif self.type == 11:
            self.imageType11()
        elif self.type == 12:
            self.imageType12()
        elif self.type == 13:
            self.imageType13()
        elif self.type == 14:
            self.imageType14()
        elif self.type == 15:
            self.imageType15()
        elif self.type == 16:
            self.imageType16()

    # Draw image type 0
    def imageType0(self):
        # Compose tile from boxes
        rect = Rect(self.w1_4, self.h1_4, self.width - self.w2_4, self.height - self.h1_4)
        pygame.gfxdraw.box(self.image, rect, self.color)

        rect = Rect(self.w3_4, self.h1_4, self.width - self.w3_4, self.height - self.h2_4)
        pygame.gfxdraw.box(self.image, rect, self.color)

    # Draw image type 1
    def imageType1(self):
        # Compose tile from boxes
        rect = Rect(0, self.h1_4, self.width, self.height - self.h2_4)
        pygame.gfxdraw.box(self.image, rect, self.color)

    # Draw image type 2
    def imageType2(self):
        # Create image type 0 and flip it
        self.imageType0()
        self.image = pygame.transform.flip(self.image, True, False)

    # Draw image type 3
    def imageType3(self):
        # Create image type 1 and rotate it
        self.imageType1()
        self.image = pygame.transform.rotate(self.image, 90)

    # Draw image type 4
    def imageType4(self):
        # Compose tile from boxes
        rect = Rect(0, self.h1_4, self.width, self.height - self.h2_4)
        pygame.gfxdraw.box(self.image, rect, self.color)
        rect = Rect(self.w1_4, 0, self.width - self.w2_4, self.height)
        pygame.gfxdraw.box(self.image, rect, self.color)

    # Draw image type 5
    def imageType5(self):
        # Create image type 0 and flip it
        self.imageType0()
        self.image = pygame.transform.flip(self.image, True, True)

    # Draw image type 6
    def imageType6(self):
        # Create image type 0 and flip it
        self.imageType0()
        self.image = pygame.transform.flip(self.image, False, True)

    # Draw image type 7
    def imageType7(self):
        # Compose tile from boxes
        rect = Rect(0, self.h1_4, self.width - self.w1_4, self.height - self.h2_4)
        pygame.gfxdraw.box(self.image, rect, self.color)

    # Draw image type 8
    def imageType8(self):
        # Create image type 7 and flip it
        self.imageType7()
        self.image = pygame.transform.flip(self.image, True, False)

    # Draw image type 9
    def imageType9(self):
        # Create image type 7 and rotate it
        self.imageType7()
        self.image = pygame.transform.rotate(self.image, -90)

    # Draw image type 10
    def imageType10(self):
        # Create image type 7 and rotate it
        self.imageType7()
        self.image = pygame.transform.rotate(self.image, 90)

    # Draw image type 11
    def imageType11(self):
        # Compose tile from boxes
        rect = Rect(self.h1_4, 0, self.width - self.w2_4, self.height)
        pygame.gfxdraw.box(self.image, rect, self.color)
        rect = Rect(self.h1_4, self.h1_4, self.width - self.h1_4, self.height - self.h2_4)
        pygame.gfxdraw.box(self.image, rect, self.color)

    # Draw image type 12
    def imageType12(self):
        # Create image type 7 and flip it
        self.imageType11()
        self.image = pygame.transform.flip(self.image, True, False)

    # Draw image type 13
    def imageType13(self):
        # Create image type 11 and rotate it
        self.imageType11()
        self.image = pygame.transform.rotate(self.image, -90)

    # Draw image type 14
    def imageType14(self):
        # Create image type 11 and rotate it
        self.imageType11()
        self.image = pygame.transform.rotate(self.image, 90)

    # Draw image type 15
    def imageType15(self):
        # Compose tile from boxes
        rect = Rect(self.h1_4, self.w1_4, self.width - self.w2_4, self.height - self.h2_4)
        pygame.gfxdraw.box(self.image, rect, self.color)

    # Draw image type 16
    def imageType16(self):
        # Compose tile from circle
        self.rect = Rect(self.rect.left + self.w1_4, self.rect.top + self.h1_4, self.h2_4, self.w2_4)
        pygame.gfxdraw.filled_circle(self.image, self.w1_4, self.h1_4, self.h1_4/2, self.color)

# Sprite representing a maze tile
class AnimatedSprite(pygame.sprite.Sprite):

    # Initialize background tile
    def __init__(self, frames, initialFrame, maxTime):
        pygame.sprite.Sprite.__init__(self)
        self.initFrameset(frames, initialFrame)
        self.maxTime = maxTime
        self.timeCheck = datetime.datetime.now()
        self.doAnimate = False
        self.doUpdate = False

    # Initializes the animation framese
    def initFrameset(self, frames, initialFrame):
        self.frames = frames
        self.currentFrame = initialFrame
        self.image = frames[initialFrame][0]
        self.rect = Rect(0, 0, frames[initialFrame][1].width, frames[initialFrame][1].height )

    # Update animated sprite
    def update(self):
        # Animate the sprite
        if self.doAnimate == True:
            currentTime = datetime.datetime.now()
            dist = currentTime - self.timeCheck
            if dist.microseconds > self.maxTime:
                self.timeCheck = currentTime
                self.currentFrame = self.currentFrame + 1
                if self.currentFrame == len(self.frames):
                    self.currentFrame = 0
                self.image, self.rect = self.frames[self.currentFrame]

# The cute hamster
class HamsterSprite(AnimatedSprite):

    # Initialize hamster sprite
    def __init__(self, background, frames, initialFrame, maxTime, xpos, ypos, xvec, yvec):
        AnimatedSprite.__init__(self, frames, initialFrame, maxTime)
        self.xpos = xpos
        self.ypos = ypos
        self.rect.left = int(self.xpos)
        self.rect.top = int(self.ypos)
        self.xvec = float(xvec)
        self.yvec = float(yvec)
        self.doAnimate = False
        self.background = background

    # Update hamster sprite
    def update(self):
        # Animate the hamster
        AnimatedSprite.update(self)

        # Clean old hamster position
        rect = Rect(self.xpos, self.ypos, self.rect.width, self.rect.height)
        pygame.gfxdraw.box(self.background, rect, (0,0,0))

        if self.xvec != 0 or self.yvec != 0:
            # Update hamster position
            self.xpos = self.xpos + self.xvec
            self.ypos = self.ypos + self.yvec
        self.rect.left = int(self.xpos)
        self.rect.top = int(self.ypos)

# The bad snake
class SnakeSprite(AnimatedSprite):

    # Initialize snake sprite
    def __init__(self, background, frames, initialFrame, maxTime, xpos, ypos, xvec, yvec):
        AnimatedSprite.__init__(self, frames, initialFrame, maxTime)
        self.xpos = xpos
        self.ypos = ypos
        self.rect.left = int(self.xpos)
        self.rect.top = int(self.ypos)
        self.xvec = float(xvec)
        self.yvec = float(yvec)
        self.background = background

    # Update snake sprite
    def update(self):
        # Animate the snake
        AnimatedSprite.update(self)

        # Clean old snacke position
        rect = Rect(self.xpos, self.ypos, self.rect.width, self.rect.height)
        pygame.gfxdraw.box(self.background, rect, (0,0,0))

        if self.xvec != 0 or self.yvec != 0:
            # Update snake position
            self.xpos = self.xpos + self.xvec
            self.ypos = self.ypos + self.yvec
        self.rect.left = int(self.xpos)
        self.rect.top = int(self.ypos)

# Used to generate sprite group containing the maze wall sprites
class HamsterMazeSpriteGenerator():

    # Initialize snail snail race maze
    def __init__(self, maze=None, xOffset=5, yOffset=5, tileWidth=20, tileHeight=20, tileColor=THECOLORS['green']):
        self.maze = maze
        self.tileWidth = tileWidth
        self.tileHeight = tileHeight
        self.tileColor = tileColor
        self.xOffset = xOffset
        self.yOffset = yOffset

    # Generate tile and grain group
    def generateGroup(self, tileGroup, grainGroup):
        dict = self.maze.fetchEnvDescriptions()
        ypos = 0
        for y in range(self.maze.height):
            xpos = 0
            for x in range(self.maze.width):
                # Empty tile
                if self.maze.fetchTile(x, y) == 0:
                    rect = Rect(xpos + self.xOffset, ypos + self.yOffset, \
                            self.tileWidth, self.tileHeight)
                    tile = MazeTile(rect, 16, THECOLORS['yellow'])
                    grainGroup.add(tile)
                    xpos = xpos + self.tileWidth
                    continue

                # Determine tile type
                rect = Rect(xpos + self.xOffset, ypos + self.yOffset, \
                            self.tileWidth, self.tileHeight)
                desc = dict[str(x) + "," + str(y)]
                if desc == '0011':
                    tileType = 0
                elif desc == '0110':
                    tileType = 1
                elif desc == '0101':
                    tileType = 2
                elif desc == '1001':
                    tileType = 3
                elif desc == '1111':
                    tileType = 4
                elif desc == '1100':
                    tileType = 5
                elif desc == '1010':
                    tileType = 6
                elif desc == '0100':
                    tileType = 7
                elif desc == '0010':
                    tileType = 8
                elif desc == '1000':
                    tileType = 9
                elif desc == '0001':
                    tileType = 10
                elif desc == '1011':
                    tileType = 11
                elif desc == '1101':
                    tileType = 12
                elif desc == '0111':
                    tileType = 13
                elif desc == '1110':
                    tileType = 14
                elif desc == '0000':
                    tileType = 15

                tile = MazeTile(rect, tileType, self.tileColor)
                tileGroup.add(tile)
                xpos = xpos + self.tileWidth
            ypos = ypos + self.tileHeight

# Main engine of the game
class HungryHamsterEngine():
    # Initialize state data instance
    def __init__(self, screenWidth=800, screenHeight=600):
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight
        self.maze = None
        self.mazeGenerator = None
        self.resourceManager = None
        self.background = None
        self.screen = None

        # Direct sprite access
        self.hamster = None

        # Sprite groups used
        self.tileGroup = pygame.sprite.RenderPlain()
        self.grainGroup = pygame.sprite.RenderPlain()
        self.hamsterGroup = pygame.sprite.RenderPlain()
        self.snakeGroup = pygame.sprite.RenderPlain()

        # Game state variables
        self.score = 0
        self.highScore = 0
        self.lives = 3

        # Maze generation parameter
        self.xstart = 17
        self.ystart = 11
        self.mwidth = 33
        self.mheight = 23
        self.mgaps = 50

        # Maze frontend parameter
        self.xoff = 5
        self.yoff = 40
        self.twidth = 24
        self.theight = 24

        # Snake movement deltas
        self.snakeXdelta = 3
        self.snakeYdelta = 3

    # Starts the pygame window
    def startWindow(self):
        # Initialize window and load resources
        self.screen = self.initWindow()
        self.resourceManager = ResourceManager('res')

        # Create empty background
        self.background = self.createEmptySurface(self.screen, self.screen.get_size())

        # Initialize the maze
        self.initMaze()

        # Define sprite group with maze tiles
        self.mazeGenerator = HamsterMazeSpriteGenerator(self.maze, self.xoff, self.yoff, \
                                                        self.twidth, self.theight, THECOLORS['pink'])
        self.mazeGenerator.generateGroup(self.tileGroup, self.grainGroup)

        # Create hamster and sprite group
        self.initHamsterSprite()

        # Create snakes and sprite group
        self.initSnakeSprites(4)

        # Enter main loop
        self.doMainLoop()

    # Initialize hamster sprite and add it to hamster group
    def initHamsterSprite(self):
        # Define sprite group with hamster
        xpos = self.xoff + self.xstart * self.twidth
        ypos = self.yoff + self.ystart * self.theight
        self.hamster = HamsterSprite(self.background, self.resourceManager.hamsterRightFrames, 0 \
                                , 500000, xpos, ypos, 0, 0)
        self.hamsterGroup.add(self.hamster)

    # Initializes the snake sprites
    def initSnakeSprites(self, count):
        # Snake start positions
        xStartPos = [1, self.mwidth-2, 1, self.mwidth-2]
        yStartPos = [1, self.mheight-2, self.mheight-2, 1]

        # Maximum 4 snakes
        if count > 4:
            count = 4
        for ndx in range(count):
            # Define sprite group with snake
            xpos = self.xoff + xStartPos[ndx] * self.twidth
            ypos = self.yoff + yStartPos[ndx] * self.theight
            snake = None
            snake = SnakeSprite(self.background, self.resourceManager.snakeRightFrames, 0 \
                                    ,500000, xpos, ypos, 0, 0)
            self.fetchSnakeVector(snake, self.hamster)
            self.snakeGroup.add(snake)

    # Initializes maze
    def initMaze(self):
        self.maze = Maze(self.mwidth, self.mheight)
        self.maze.generateMaze(self.xstart, self.ystart, self.mgaps)

    # Init the pygame window
    def initWindow(self):
        pygame.init()
        screen = pygame.display.set_mode((self.screenWidth, self.screenHeight))
        pygame.display.set_caption('Hungry Hamster')
        pygame.mouse.set_visible(0)
        return screen

    # Create an empty background
    def createEmptySurface(self, screen, rect):
        background = pygame.Surface(rect)
        background = background.convert()
        background.fill((0, 0, 0))
        return background

    # Check if hamster has collided with tiles
    def checkHamsterMazeTileCollisions(self, oldXPos=0, oldYPos=0):
        collgroup=pygame.sprite.spritecollide(self.hamster, self.tileGroup, 0, pygame.sprite.collide_mask)

        if len(collgroup) > 0:
            # Clean hamster background
            rect = Rect(self.hamster.xpos, self.hamster.ypos, self.hamster.rect.width, self.hamster.rect.height)
            pygame.gfxdraw.box(self.background, rect, (0,0,0))
            self.screen.blit(self.background, (0,0))

            # Reset hamster position
            self.hamster.xpos = oldXPos
            self.hamster.ypos = oldYPos
            self.hamster.xvec = 0
            self.hamster.yvec = 0
            self.hamster.doAnimate = False

    # Check if snake has collided with tile
    def checkSnakeMazeTileCollisions(self):
        snakes = self.snakeGroup.sprites()
        for ndx in range(len(snakes)):
            snake = snakes[ndx]

            # Calculate next step snake position in maze
            #xsnakeLeft = snake.xpos
            #xsnakeRight = snake.xpos + snake.rect.width
            #ysnakeTop = snake.ypos
            #ysnakeBottom = snake.ypos + snake.rect.height

            xsnakeLeft = int(snake.xpos + ((snake.rect.width - self.twidth) / 2))
            xsnakeRight = int(snake.xpos + snake.rect.width - ((snake.rect.width - self.twidth) / 2))
            ysnakeTop = int(snake.ypos +  ((snake.rect.height - self.theight) / 2))
            ysnakeBottom = int(snake.ypos + snake.rect.height - ((snake.rect.height - self.theight) / 2))

            # Fetch tile to check if snake will collide with wall
            if snake.xvec < 0:
                xsnakeMaze = int((xsnakeLeft + snake.xvec - self.xoff) / self.twidth)
                ysnakeMaze = int((ysnakeTop - self.yoff) / self.theight)
            elif snake.xvec > 0:
                xsnakeMaze = int((xsnakeRight + snake.xvec - self.xoff) / self.twidth)
                ysnakeMaze = int((ysnakeTop - self.yoff) / self.theight)
            elif snake.yvec < 0:
                xsnakeMaze = int((xsnakeLeft - self.xoff) / self.twidth)
                ysnakeMaze = int((ysnakeTop + snake.yvec - self.yoff) / self.theight)
            elif snake.yvec > 0:
                xsnakeMaze = int((xsnakeLeft - self.xoff) / self.twidth)
                ysnakeMaze = int((ysnakeBottom + snake.yvec - self.yoff) / self.theight)

            tile = self.maze.fetchTile(xsnakeMaze, ysnakeMaze)
            if tile == 1:
                # Clean snake background
                rect = Rect(snake.xpos, snake.ypos, snake.rect.width, snake.rect.height)
                pygame.gfxdraw.box(self.background, rect, (0,0,0))
                self.screen.blit(self.background, (0,0))

                # Rescue old snake vector
                oldXVec = snake.xvec
                oldYVec = snake.yvec

                # Fetch new snake vector
                self.fetchSnakeVector(snake, self.hamster)

                # Correct snake position by old vector when direction
                # change between horizontal and vertical
                if snake.xvec != 0 and oldYVec != 0:
                    snake.ypos = snake.ypos + oldYVec
                elif snake.yvec != 0 and oldXVec != 0:
                    snake.xpos = snake.xpos + oldXVec



    # Check if hamster has collided with tiles
    def checkHamsterGrainTileCollisions(self):
        collgroup=pygame.sprite.spritecollide(self.hamster, self.grainGroup, 1, pygame.sprite.collide_circle)
        if len(collgroup) > 0:
            grain = collgroup[0]
            pygame.gfxdraw.box(self.background, grain.rect, (0,0,0))
            self.screen.blit(self.background, (0,0))
            self.score = self.score + 1
            self.grainGroup.remove(grain)

    def fetchSnakeVector(self, snake, hamster):
        # Calculate snake and hamster position in maze
        xsnakeMaze = (snake.xpos + snake.rect.width / 2 - self.xoff) / self.twidth
        ysnakeMaze = (snake.ypos + snake.rect.height / 2 - self.yoff) / self.theight
        xhamsterMaze = (hamster.xpos + hamster.rect.width / 2 - self.xoff) / self.twidth
        yhamsterMaze = (hamster.ypos + hamster.rect.height / 2 - self.yoff) / self.theight

        # Snake postion matches hamster position
        if xsnakeMaze == xhamsterMaze and ysnakeMaze == yhamsterMaze:
            snake.xvec = 0
            snake.yvec = 0
            return

        # Fetch path from snake to hamster
        path = self.maze.findWay(int(xsnakeMaze), int(ysnakeMaze), int(xhamsterMaze), int(yhamsterMaze))

        # Determine snake movement vector
        xdiff = xsnakeMaze - path[1][0]
        ydiff = ysnakeMaze - path[1][1]
        if xdiff < 0:
            snake.xvec = self.snakeXdelta
            snake.yvec = 0
        elif xdiff > 0:
            snake.xvec = -self.snakeXdelta
            snake.yvec = 0
        elif ydiff < 0:
            snake.xvec = 0
            snake.yvec = self.snakeYdelta
        elif ydiff > 0:
            snake.xvec = 0
            snake.yvec = -self.snakeXdelta

    # Process main loop
    def doMainLoop(self):

        doLoop = True
        clock = time.Clock()
        oldHamsterXPos = 0
        oldHamsterYPos = 0
        while doLoop:
            clock.tick(60) # fps

            # Avoid hamster going through walls
            self.checkHamsterMazeTileCollisions(oldHamsterXPos, oldHamsterYPos)

            self.checkSnakeMazeTileCollisions()

            # Check hamster eating grain
            self.checkHamsterGrainTileCollisions()

            # Catch input event
            oldHamsterXVec = self.hamster.xvec
            oldHamsterXPos = self.hamster.xpos
            oldHamsterYPos = self.hamster.ypos
            for event in pygame.event.get():
                if event.type == QUIT:
                    doLoop = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        doLoop = False
                    elif event.key == 273: # up
                        self.hamster.xvec = 0
                        self.hamster.yvec = -5
                        self.hamster.doAnimate = True
                    elif event.key == 274: # down
                        self.hamster.xvec = 0
                        self.hamster.yvec = 5
                        self.hamster.doAnimate = True
                    elif event.key == 275: # right
                        self.hamster.yvec = 0
                        self.hamster.xvec = 5
                        self.hamster.frames = self.resourceManager.hamsterRightFrames
                        self.hamster.doAnimate = True
                        if oldHamsterXVec <= 0:
                            self.hamster.initFrameset(self.hamster.frames, 0)
                    elif event.key == 276: # left
                        self.hamster.yvec = 0
                        self.hamster.xvec = -5
                        self.hamster.frames = self.resourceManager.hamsterLeftFrames
                        self.hamster.doAnimate = True
                        if oldHamsterXVec >= 0:
                            self.hamster.initFrameset(self.hamster.frames, 0)
                elif event.type == KEYUP:
                    self.hamster.xvec = 0
                    self.hamster.yvec = 0
                    self.hamster.doAnimate = False

            # Update sprite groups
            self.hamsterGroup.update()
            self.snakeGroup.update()
            self.tileGroup.update()
            self.grainGroup.update()

            # Update screen
            self.tileGroup.draw(self.background)
            self.hamsterGroup.draw(self.background)
            self.grainGroup.draw(self.background)
            self.snakeGroup.draw(self.background)

            self.screen.blit(self.background, (0,0))
            pygame.display.flip()


# Entrypoint
def main():

    # Start maze pygrame frontend
    hungryHamsterEngine = HungryHamsterEngine(800, 600)
    hungryHamsterEngine.startWindow()
    sys.exit(0)

#this calls the 'main' function when this script is executed
if __name__ == '__main__': main()