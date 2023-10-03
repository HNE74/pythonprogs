import pgzrun
import os
from enum import Enum
import random

# Direction enum
class Direction(Enum):
    NORTH = 0
    SOUTH = 1
    WEST = 2
    EAST = 3

    # Get the opposite direction
    def opposite(self):
        if self == Direction.NORTH:
            return Direction.SOUTH
        elif self == Direction.SOUTH:
            return Direction.NORTH
        elif self == Direction.EAST:
            return Direction.WEST
        elif self == Direction.WEST:
            return Direction.EAST

    # Get MazeCell in a given direction
    def to_cell(self, cell):
        if self == Direction.NORTH:
            return cell.neighbors[0]
        elif self == Direction.SOUTH:
            return cell.neighbors[1]
        elif self == Direction.WEST:
            return cell.neighbors[2]
        elif self == Direction.EAST:
            return cell.neighbors[3]

# A Maze Cell   
class MazeCell: 

    #constructor method
    def __init__(self, i, wp, hp, w=20, h=20):
        self.i = i
        self.w = w
        self.h = h
        self.x = i % wp
        self.y = i // wp
        self.visited = False
        self.walls = [True, True, True, True]
        self.neighbors = []   

    #draw the cell
    def draw(self, screen, xoffset, yoffset):
        x = self.x * self.w + xoffset
        y = self.y * self.h + yoffset

        if self.walls[0]:
            screen.draw.line((x, y), (x + self.w, y), (255, 255, 255))
        if self.walls[1]:
            screen.draw.line((x, y + self.h), (x + self.w, y + self.h), (255, 255, 255))
        if self.walls[2]:
            screen.draw.line((x, y), (x, y + self.h), (255, 255, 255))
        if self.walls[3]:
            screen.draw.line((x + self.w, y), (x + self.w, y + self.h), (255, 255, 255))

# A Maze is a collection of MazeCells
class Maze:
    # Constructor
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.cells = []
        self.stack = []
        self.current = None

        # Create the cells
        for i in range(w * h):
            self.cells.append(MazeCell(i, w, h))

        # Set the current cell
        self.current = self.cells[0]

        # Assign neighbors
        self.assign_neighbors()
    
    def assign_neighbors(self):
        for cell in self.cells:
            x = cell.x
            y = cell.y
            cell.neighbors.append(self.get_cell(x, y - 1))
            cell.neighbors.append(self.get_cell(x, y + 1))
            cell.neighbors.append(self.get_cell(x - 1, y))
            cell.neighbors.append(self.get_cell(x + 1, y))
    
    # Connect cell with neighbor in given direction
    def connect(self, cell, direction):
        neighbor = direction.to_cell(cell)
        if neighbor:
            cell.walls[direction.value] = False
            neighbor.walls[direction.opposite().value] = False
    
    # Get cell at x, y
    def get_cell(self, x, y):
        if x < 0 or x >= self.w or y < 0 or y >= self.h:
            return None
        else:
            return self.cells[x + y * self.w]
    
    # Draw the maze
    def draw(self, screen, xoffset, yoffset):
        for cell in self.cells:
            cell.draw(screen, xoffset, yoffset)


def create_binary_tree_maze(maze):
    for xp in range(maze.w):
        for yp in range(maze.h):
            cell = maze.get_cell(xp, yp)
            if cell:
                if xp == maze.w - 1 and yp == maze.h - 1:
                    continue
                elif xp == maze.w - 1:
                    maze.connect(cell, Direction.SOUTH)
                elif yp == maze.h - 1:
                    maze.connect(cell, Direction.EAST)
                else:
                    if random.randint(0, 1) == 0:
                        maze.connect(cell, Direction.SOUTH)
                    else:
                        maze.connect(cell, Direction.EAST)


def update():
    # Your game logic here
    pass

def draw():
    screen.clear()
    maze.draw(screen,50,50) 

def on_key_down(key):
    if key == keys.ESCAPE:  # You can change this to any key you want
        exit()

maze = Maze(5, 5)
create_binary_tree_maze(maze)
os.environ['SDL_VIDEO_CENTERED'] = '1'
pgzrun.go()