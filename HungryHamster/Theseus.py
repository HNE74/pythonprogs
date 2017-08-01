import sys, os, pygame, random
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

        # Create maze without corridors
        self.maze=[]
        for y in range(self.height):
            line = []
            self.maze.append(line)
            for x in range(self.width):
                line.append(1)

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

    # Recursively fetches paths to the target, path might not have
    # optimal length
    def fetchPathToTargetRec(self, xpos, ypos, xend, yend, cnt, maze):
        # Vectors to check adjacent tiles
        global toCheckX
        global toCheckY

        # Abort search if shorter path has been found
        if cnt >= self.minFound:
            return

        # Apply counter to current tile
        self.setTile(xpos, ypos, cnt, maze)

        # Abort if target reached
        if xpos == xend and ypos == yend:
            self.minFound = cnt
            return

        # Check adjacent tiles
        for ndx in range(len(toCheckX)):
            tile = self.fetchTile(xpos+toCheckX[ndx], ypos+toCheckY[ndx], maze)
            if tile == 0:
                self.fetchPathToTargetRec(xpos+toCheckX[ndx], ypos+toCheckY[ndx], \
                               xend, yend, cnt+1, maze)

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
        while(cnt < gaps and len(tiles) > 0):
            ndx = random.randint(0, len(tiles)-1)
            self.setTile(tiles[ndx][0], tiles[ndx][1], 0)
            tiles.remove(tiles[ndx])
            cnt = cnt + 1

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

# Pygames based frontend to maze generator for demonstration
class MazeFrontend():

    # Initialize state data instance
    def __init__(self, screenWidth=800, screenHeight=600, maze=None):
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight
        self.labyrinth = maze
        self.tileHeight = 15
        self.tileWidth = 15
        self.labTop = 100
        self.labLeft = 15
        self.selectState = 0
        self.startPoint = None
        self.endPoint = None

    # Starts the pygame window
    def startWindow(self):
        # Initialize window
        screen = self.initWindow()

        # Create empty background
        background = self.createEmptySurface(screen, screen.get_size())

        # Enter main loop
        self.doMainLoop(screen, background)

    # Init the pygame window
    def initWindow(self):
        pygame.init()
        screen = pygame.display.set_mode((self.screenWidth, self.screenHeight))
        pygame.display.set_caption('Theseus V1.0')
        pygame.mouse.set_visible(1)
        return screen

    # Create an empty background
    def createEmptySurface(self, screen, rect):
        background = pygame.Surface(rect)
        background = background.convert()
        background.fill((0, 0, 0))
        return background

    # Prints the maze to the provided background
    def printMaze(self, background, labyrinth, path):
        # Iterate over maze tiles and print them to background
        xpos=self.labLeft
        ypos=self.labTop
        for y in range(labyrinth.height):
            line = labyrinth.maze[y]
            for x in range(labyrinth.width):
                rect = Rect(xpos, ypos, self.tileWidth, self.tileHeight)
                if line[x] == 1:
                    pygame.gfxdraw.box(background, rect, THECOLORS['orange'])
                else:
                    pygame.gfxdraw.box(background, rect, THECOLORS['black'])
                if path != None:
                    # Check if position in path
                    for ndx in range(len(path)):
                        coord = path[ndx]
                        xc = coord[0]
                        yc = coord[1]
                        if xc == x and yc == y:
                            pygame.gfxdraw.box(background, rect, THECOLORS['green'])

                xpos = xpos + self.tileWidth

            xpos = self.labLeft
            ypos = ypos + self.tileHeight

    # Fetches the maze tile coordinates from the current
    # mouse position
    def fetchMazeCoordinatesFromMouse(self):
        # Get current mouse position
        mousePos = pygame.mouse.get_pos()

        # Check if mouse is not on maze
        labRight = self.labLeft + self.labyrinth.width * self.tileWidth
        labBottom = self.labTop + self.labyrinth.height * self.tileHeight
        if mousePos[0] < self.labLeft or mousePos[1] < self.labTop or \
           mousePos[0] > labRight or mousePos[1] > labBottom:
               return None

        # Calculate tile coordinates
        xTile = (mousePos[0] - self.labLeft) / self.tileWidth
        yTile = (mousePos[1] - self.labTop) / self.tileHeight
        return [xTile, yTile]

    # Handles mousclick on lab
    def handleLabMouseClick(self, coord, background):
        # Ignore click on wall
        if self.labyrinth.fetchTile(coord[0], coord[1]) == 1:
            return

        # Set coordinates for waypoint search
        if self.selectState == 0:
            self.startPoint = coord
            self.selectState = 1
        elif self.selectState == 1:
            self.endPoint = coord
            path = self.labyrinth.findWay(self.startPoint[0],self.startPoint[1], \
                                          self.endPoint[0], self.endPoint[1])
            self.printMaze(background, self.labyrinth, path)
            self.selectState = 0

    # Process main loop
    def doMainLoop(self, screen, background):
        # Print maze to background
        self.printMaze(background, self.labyrinth, None)

        doLoop = True
        clock = time.Clock()
        while doLoop:
            clock.tick(100) # fps

            # Catch input event
            for event in pygame.event.get():
                if event.type == QUIT:
                    doLoop = False
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    doLoop = False
                elif event.type == MOUSEBUTTONDOWN:
                    coord = self.fetchMazeCoordinatesFromMouse()
                    if coord != None:
                        self.handleLabMouseClick(coord, background)

            # Update screen
            screen.blit(background, (0,0))
            pygame.display.flip()

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
        self.createTileImage()

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
        rect = Rect(0, self.h1_4, self.width - self.w2_4, self.height - self.h2_4)
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

# Pygames based frontend to maze generator for demonstration
class TileFrontend():

    # Initialize state data instance
    def __init__(self, screenWidth=800, screenHeight=600):
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight
        self.screen = None
        self.background = None

    # Starts the pygame window
    def startWindow(self):
        # Initialize window
        self.screen = self.initWindow()

        # Create empty background
        self.background = self.createEmptySurface(self.screen.get_size())

        # Enter main loop
        self.doMainLoop()

    # Init the pygame window
    def initWindow(self):
        pygame.init()
        screen = pygame.display.set_mode((self.screenWidth, self.screenHeight))
        pygame.display.set_caption('Tile Frontend')
        pygame.mouse.set_visible(1)
        return screen

    # Create an empty background
    def createEmptySurface(self, rect):
        background = pygame.Surface(rect)
        background = background.convert()
        background.fill((0, 0, 0))
        return background

    # Prints tiles to background
    def printTiles(self, tileGroup):
        rect = Rect(10, 10, 30, 30)
        tile = MazeTile(rect, 0, THECOLORS['green'])
        tileGroup.add(tile)

        rect = Rect(45, 10, 30, 30)
        tile = MazeTile(rect, 1, THECOLORS['green'])
        tileGroup.add(tile)

        rect = Rect(80, 10, 30, 30)
        tile = MazeTile(rect, 2, THECOLORS['lightblue'])
        tileGroup.add(tile)

        rect = Rect(10, 45, 30, 30)
        tile = MazeTile(rect, 3, THECOLORS['green'])
        tileGroup.add(tile)

        rect = Rect(10, 80, 30, 30)
        tile = MazeTile(rect, 4, THECOLORS['green'])
        tileGroup.add(tile)

        rect = Rect(80, 80, 30, 30)
        tile = MazeTile(rect, 5, THECOLORS['green'])
        tileGroup.add(tile)

        rect = Rect(45, 115, 30, 30)
        tile = MazeTile(rect, 6, THECOLORS['green'])
        tileGroup.add(tile)

        rect = Rect(45, 80, 30, 30)
        tile = MazeTile(rect, 7, THECOLORS['green'])
        tileGroup.add(tile)

        rect = Rect(80, 115, 30, 30)
        tile = MazeTile(rect, 8, THECOLORS['green'])
        tileGroup.add(tile)

        rect = Rect(10, 115, 30, 30)
        tile = MazeTile(rect, 9, THECOLORS['green'])
        tileGroup.add(tile)

        rect = Rect(80, 45, 30, 30)
        tile = MazeTile(rect, 10, THECOLORS['green'])
        tileGroup.add(tile)

    # Process main loop
    def doMainLoop(self):
        # Print maze to background
        tileGroup = pygame.sprite.RenderPlain()
        self.printTiles(tileGroup)

        doLoop = True
        clock = time.Clock()
        while doLoop:
            clock.tick(100) # fps

            # Catch input event
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit(0)
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    sys.exit(0)

            # Update screen
            self.screen.blit(self.background, (0,0))
            tileGroup.draw(self.screen)
            pygame.display.flip()


# Entrypoint
def main():
    #maze = Maze(51, 31)
    #maze.generateMaze(5, 5, 50)
    #maze.generateTestMaze()
    #path = maze.findWay(1,1,41,17)

    # Print result to console
    #maze.printMazeWithPath(path)

    # Start maze pygrame frontend
    frontend = TileFrontend(800, 600)
    frontend.startWindow()

#this calls the 'main' function when this script is executed
if __name__ == '__main__': main()