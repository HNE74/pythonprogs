##########################################################
### Theseus V1.0
### by Heiko Nolte / February 2010
### Implementation of a random maze generation algorithm
### with pygame frontend to visualize it. Also implements
### the Lee algorithm to find the shortest way between to
### points in the maze.
### This code is distributed under
### GNU GENERAL PUBLIC LICENSE, Version 3.
##########################################################

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
        self.labTop = 80
        self.labLeft = 15
        self.selectState = 0
        self.startPoint = None
        self.endPoint = None
        self.path = None
        self.buttons=[]
        self.refreshMaze = False
        self.gaps = 10

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
        pygame.display.set_caption('Theseus V1.0 / by Heiko Nolte')
        pygame.mouse.set_visible(1)
        return screen

    # Inits the controls to be added to screen
    def initControls(self):

        # Decrease maze size button
        btn = DecWidthButton(125, 17, 40, 40, 'ARROW_LEFT', self, THECOLORS['white'])
        self.buttons.append(btn)

        # Increase maze size button
        btn = IncWidthButton(180, 17, 40, 40, 'ARROW_RIGHT', self, THECOLORS['white'], self)
        self.buttons.append(btn)

        # Increase height button
        btn = DecHeightButton(422, 17, 40, 40, 'ARROW_LEFT', self, THECOLORS['white'], self)
        self.buttons.append(btn)

        # Decrease height button
        btn = IncHeightButton(477, 17, 40, 40, 'ARROW_RIGHT', self, THECOLORS['white'], self)
        self.buttons.append(btn)

        # Increase gaps button
        btn = DecGapsButton(682, 17, 40, 40, 'ARROW_LEFT', self, THECOLORS['white'], self)
        self.buttons.append(btn)

        # Decrease gaps button
        btn = IncGapsButton(737, 17, 40, 40, 'ARROW_RIGHT', self, THECOLORS['white'], self)
        self.buttons.append(btn)

    # Create an empty background
    def createEmptySurface(self, screen, rect):
        background = pygame.Surface(rect)
        background = background.convert()
        background.fill((0, 0, 0))
        return background

    # Prints controls on top of screen
    def printControls(self, background):

        font=pygame.font.Font("fonts/digit.ttf", 38)
        text=font.render("Width:", 2, THECOLORS['white'])
        background.blit(text, (15, 15))

        text=font.render("Height:", 2, THECOLORS['white'])
        background.blit(text, (300, 15))

        text=font.render("Gaps:", 2, THECOLORS['white'])
        background.blit(text, (580, 15))

        for b in range(len(self.buttons)):
            button = self.buttons[b]
            button.drawButton(background)

    # Prints the maze to the provided background
    def printMaze(self, background, labyrinth, path, coord):
        # Maze position on screen
        xpos=self.labLeft
        ypos=self.labTop

        # Iterate over maze tiles and print them to background
        if self.refreshMaze == True:
            rect = Rect(self.labLeft, self.labTop, \
                        self.tileWidth * self.labyrinth.oldWidth, \
                        self.tileHeight * self.labyrinth.oldHeight)
            pygame.gfxdraw.box(background, rect, THECOLORS['black'])
            self.refreshMaze = False

        # Iterate over maze tiles and print them to background

        for y in range(labyrinth.height):
            line = labyrinth.maze[y]
            for x in range(labyrinth.width):
                rect = Rect(xpos, ypos, self.tileWidth, self.tileHeight)
                if line[x] == 1:
                    # Draw wall
                    pygame.gfxdraw.box(background, rect, THECOLORS['orange'])
                else:
                    # Draw gap
                    pygame.gfxdraw.box(background, rect, THECOLORS['black'])

                # Draw path from startpoint to endpoint
                if path != None:
                    # Check if position in path
                    for ndx in range(len(path)):
                        pcoord = path[ndx]
                        if pcoord[0] == x and pcoord[1] == y:
                            pygame.gfxdraw.box(background, rect, THECOLORS['green'])

                if coord != None and x == coord[0] and y == coord[1] \
                   and line[x] != 1:
                    # Draw cursor
                    pygame.gfxdraw.box(background, rect, THECOLORS['red'])

                if self.selectState == 1 and self.startPoint != None and \
                     x == self.startPoint[0] and y == self.startPoint[1]:
                    # Draw start point
                    pygame.gfxdraw.box(background, rect, THECOLORS['yellow'])

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
    def handleLabMouseClick(self, coord):
        # Ignore click on wall
        if self.labyrinth.fetchTile(coord[0], coord[1]) == 1:
            return

        # Set coordinates for waypoint search
        if self.selectState == 0:
            self.startPoint = coord
            self.selectState = 1
            self.path = None
        elif self.selectState == 1:
            self.endPoint = coord
            self.path = self.labyrinth.findWay(self.startPoint[0],self.startPoint[1], \
                                          self.endPoint[0], self.endPoint[1])
            self.selectState = 0

    # Process main loop
    def doMainLoop(self, screen, background):

        # Create control buttons
        self.initControls()

        doLoop = True
        clock = time.Clock()
        while doLoop:
            clock.tick(100) # fps

            # Retrieve selected tile
            coord = self.fetchMazeCoordinatesFromMouse()

            # Catch input event
            for event in pygame.event.get():
                if event.type == QUIT:
                    doLoop = False
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    doLoop = False
                elif event.type == MOUSEBUTTONDOWN:
                    if coord != None:
                        # Mouse click on maz
                        self.handleLabMouseClick(coord)
                    else:
                        # Mouse click on button
                        for ndx in range(len(self.buttons)):
                            button = self.buttons[ndx]
                            button.handleMouseClick()

            # Update screen
            self.printControls(background)
            self.printMaze(background, self.labyrinth, self.path, coord)
            screen.blit(background, (0,0))
            pygame.display.flip()


# Button to set maze generation parameter
# Allowed types are: 'ARROW_RIGHT', 'ARROW_LEFT', 'TEXT'
class Button():

    # Initialize state data instance
    def __init__(self, xpos=10, ypos=10, width=80, height=50, \
                 btype='ARROW_RIGHT', container=None, color=None, text=None):
        self.xpos = xpos
        self.ypos = ypos
        self.width = width
        self.height = height
        self.btype = btype
        self.text = text
        self.color = color
        self.container = container

        # Check if passed button type is correct
        if btype != 'ARROW_RIGHT' and btype != 'ARROW_LEFT' and \
            btype != 'TEXT':
                raise Exception('Invalid button type.')

        # Check if passed button type is correct
        if color == None:
            raise Exception('Button color not set.')

    # Handles mouse click event
    def handleMouseClick(self):
        # Fetch mouse position
        coord = pygame.mouse.get_pos()

        # Abort if mouse not over button
        if coord[0] < self.xpos or coord[0] > self.xpos + self.width or \
           coord[1] < self.ypos or coord[1] > self.ypos + self.height:
               return
        else:
            # Invoke action when button clicked
            self.buttonClicked(coord)

    # To be overwritten by subclass
    def buttonClicked(self, coord):
        pass

    # Draws the provided button onto background
    def drawButton(self, background):
        # Fetch button background
        size = (self.width, self.height)
        btnBackground = self.createEmptySurface(size)

        # Draw border rectangle
        rect = Rect(0, 0, self.width, self.height)
        pygame.gfxdraw.rectangle(btnBackground, rect, self.color)

        # Handle different button types
        points = []
        if self.btype == 'ARROW_RIGHT' or self.btype == 'ARROW_LEFT':
            btnBackground = self.drawArrow(btnBackground)

        # Draw button to background
        background.blit(btnBackground, (self.xpos, self.ypos))

    # Create an empty background
    def createEmptySurface(self, size):
        background = pygame.Surface(size)
        background = background.convert()
        background.fill((0, 0, 0))
        return background

    # Draws an arrow onto the background
    def drawArrow(self, background):

        # Draw arrow
        points = []
        x = 5
        y = self.height / 2
        points.append((x,y))

        y = y - self.height / 5
        points.append((x,y))

        x = x + self.width - 25
        points.append((x,y))

        y = 5
        points.append((x,y))

        x = self.width - 5
        y = self.height / 2
        points.append((x,y))

        x = self.width - 20
        y = self.height - 5
        points.append((x,y))

        y = (self.height / 5) * 3 + 5
        points.append((x,y))

        x = 5
        points.append((x,y))

        x = 5
        y = self.height / 2
        points.append((x,y))
        pygame.gfxdraw.filled_polygon(background, points, self.color)

        # Flip arrow
        if self.btype == 'ARROW_LEFT':
            background = pygame.transform.flip(background, True, True)

        return background

# Increase maze width
class DecWidthButton(Button):

    # Initialize button
    def __init__(self, xpos=10, ypos=10, width=80, height=50, \
                 btype='ARROW_RIGHT', container=None, color=None, text=None):
        # Call super class constructor
        Button.__init__(self, xpos, ypos, width, height, \
                        btype, container, color, text)

    # Increase maze width
    def buttonClicked(self, coord):
        maze = self.container.labyrinth
        if maze.width > 11:
            maze.oldWidth = maze.width
            maze.oldHeight = maze.height
            maze.width = maze.width - 2
            maze.generateMaze(1, 1, self.container.gaps)
            self.container.path = None
            self.container.refreshMaze = True

# Increase maze width
class IncWidthButton(Button):

    # Initialize button
    def __init__(self, xpos=10, ypos=10, width=80, height=50, \
                 btype='ARROW_RIGHT', container=None, color=None, text=None):
        # Call super class constructor
        Button.__init__(self, xpos, ypos, width, height, \
                        btype, container, color, text)

    # Increase maze width
    def buttonClicked(self, coord):
        maze = self.container.labyrinth
        if maze.width < 51:
            maze.oldWidth = maze.width
            maze.oldHeight = maze.height
            maze.width = maze.width + 2
            maze.generateMaze(1, 1, self.container.gaps)
            self.container.path = None
            self.container.refreshMaze = True

# Decrease maze height
class DecHeightButton(Button):

    # Initialize button
    def __init__(self, xpos=10, ypos=10, width=80, height=50, \
                 btype='ARROW_RIGHT', container=None, color=None, text=None):
        # Call super class constructor
        Button.__init__(self, xpos, ypos, width, height, \
                        btype, container, color, text)

    # Decrease maze height
    def buttonClicked(self, coord):
        maze = self.container.labyrinth
        if maze.height > 11:
            maze.oldWidth = maze.width
            maze.oldHeight = maze.height
            maze.height = maze.height - 2
            maze.generateMaze(1, 1, self.container.gaps)
            self.container.path = None
            self.container.refreshMaze = True

# Increases maze height
class IncHeightButton(Button):

    # Initialize button
    def __init__(self, xpos=10, ypos=10, width=80, height=50, \
                 btype='ARROW_RIGHT', container=None, color=None, text=None):
        # Call super class constructor
        Button.__init__(self, xpos, ypos, width, height, \
                        btype, container, color, text)

    # Increase maze height
    def buttonClicked(self, coord):
        maze = self.container.labyrinth
        if maze.height < 33:
            maze.oldWitdth = maze.width
            maze.oldHeight = maze.height
            maze.height = maze.height + 2
            maze.generateMaze(1, 1, self.container.gaps)
            self.container.path = None
            self.container.refreshMaze = True

# Increases number of gaps
class IncGapsButton(Button):

    # Initialize button
    def __init__(self, xpos=10, ypos=10, width=80, height=50, \
                 btype='ARROW_RIGHT', container=None, color=None, text=None):
        # Call super class constructor
        Button.__init__(self, xpos, ypos, width, height, \
                        btype, container, color, text)

    # Increase number of gaps
    def buttonClicked(self, coord):
        maze = self.container.labyrinth
        maze.oldWidth = maze.width
        maze.oldHeight = maze.height
        self.container.gaps = self.container.gaps + 5
        maze.generateMaze(1, 1, self.container.gaps)
        self.container.path = None
        self.container.refreshMaze = True

# Increases number of gaps
class DecGapsButton(Button):

    # Initialize button
    def __init__(self, xpos=10, ypos=10, width=80, height=50, \
                 btype='ARROW_RIGHT', container=None, color=None, text=None):
        # Call super class constructor
        Button.__init__(self, xpos, ypos, width, height, \
                        btype, container, color, text)

    # Decrease number of gaps
    def buttonClicked(self, coord):
        maze = self.container.labyrinth
        if self.container.gaps > 0:
            maze.oldWidth = maze.width
            maze.oldHeight = maze.height
            self.container.gaps = self.container.gaps - 5
            maze.generateMaze(1, 1, self.container.gaps)
            self.container.path = None
            self.container.refreshMaze = True

# Entrypoint
def main():
    maze = Maze(51, 33)
    maze.generateMaze(5, 5, 10)
    #maze.generateTestMaze()
    path = maze.findWay(1,1,41,17)

    # Print result to console
    #maze.printMazeWithPath(path)

    # Start maze pygrame frontend
    frontend = MazeFrontend(800, 600, maze)
    frontend.startWindow()
    sys.exit(0)

#this calls the 'main' function when this script is executed
if __name__ == '__main__': main()