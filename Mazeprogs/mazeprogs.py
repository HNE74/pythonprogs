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

    # Connect two cells
    def connect_neighbor(self, cell1, cell2):
        if cell1.x == cell2.x:
            if cell1.y == cell2.y - 1:
                self.connect(cell1, Direction.SOUTH)
            elif cell1.y == cell2.y + 1:
                self.connect(cell1, Direction.NORTH)
        elif cell1.y == cell2.y:
            if cell1.x == cell2.x - 1:
                self.connect(cell1, Direction.EAST)
            elif cell1.x == cell2.x + 1:
                self.connect(cell1, Direction.WEST)
    
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

# Apply the binary tree algorithm to the maze
def apply_binary_tree_algorithm(maze):
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

# Apply the sidewinder algorithm to the maze
def apply_sidewinder_algorithm(maze):
    for yp in range(maze.h):
        run = []
        for xp in range(maze.w):
            cell = maze.get_cell(xp, yp)
            if cell:
                run.append(cell)
                at_eastern_boundary = xp == maze.w - 1
                at_southern_boundary = yp == maze.h - 1
                should_close_out = at_eastern_boundary \
                    or (not at_southern_boundary and random.randint(0, 1) == 0)
                if should_close_out:
                    member = random.choice(run)
                    if member:
                        maze.connect(member, Direction.SOUTH)
                    run.clear()
                else:
                    maze.connect(cell, Direction.EAST)

# Apply the recursive backtracking algorithm to the maze
def apply_recursive_backtracking_algorithm(maze):
    while True:
        if maze.current:
            maze.current.visited = True
            unvisited_neighbors = []
            for neighbor in maze.current.neighbors:
                if neighbor and not neighbor.visited:
                    unvisited_neighbors.append(neighbor)
            if len(unvisited_neighbors) > 0:
                neighbor = random.choice(unvisited_neighbors)
                maze.stack.append(maze.current)
                maze.connect_neighbor(maze.current, neighbor)
                maze.current = neighbor
            elif len(maze.stack) > 0:
                maze.current = maze.stack.pop()
            else:
                break
        else:
            break

def apply_hunt_and_kill_algorithm(maze):
    maze.current = maze.cells[0]
    while True:
        if maze.current:
            maze.current.visited = True
            unvisited_neighbors = []
            for neighbor in maze.current.neighbors:
                if neighbor and not neighbor.visited:
                    unvisited_neighbors.append(neighbor)
            if len(unvisited_neighbors) > 0:
                neighbor = random.choice(unvisited_neighbors)
                maze.connect_neighbor(maze.current, neighbor)
                maze.current = neighbor
            else:
                maze.current = None
                for cell in maze.cells:
                    if not cell.visited:
                        visited_neighbors = []
                        for neighbor in cell.neighbors:
                            if neighbor and neighbor.visited:
                                visited_neighbors.append(neighbor)
                        if len(visited_neighbors) > 0: 
                            maze.connect_neighbor(cell, random.choice(visited_neighbors))
                            maze.current = cell
                            break
                if not maze.current:
                    break
        else:
            break
   
def update():
    # Your game logic here
    pass

def draw():
    screen.clear()
    screen.draw.text("Algorithm: " + get_algorithm_name(algorithms[selected_algorithm]), (50, 20), color="white")
    maze.draw(screen,50,50) 

def on_key_down(key):
    if key == keys.ESCAPE:  # You can change this to any key you want
        exit()
    if key == keys.SPACE: # Recreate the maze
        global maze
        maze = Maze(maze_with, maze_height)
        
        # select an algorithm by index
        global selected_algorithm
        selected_algorithm += 1
        if selected_algorithm >= len(algorithms):
            selected_algorithm = 0
        algorithms[selected_algorithm](maze)
   
# remove apply_ from and underscore from function name
def get_algorithm_name(algorithm):
    return algorithm.__name__.replace("apply", "").replace("_", " ").replace("algorithm", "")

# add algorithms functions to list
algorithms = []
algorithms.append(apply_binary_tree_algorithm)
algorithms.append(apply_sidewinder_algorithm)
algorithms.append(apply_recursive_backtracking_algorithm)
algorithms.append(apply_hunt_and_kill_algorithm)
global selected_algorithm
selected_algorithm = 0

maze_with, maze_height = 20, 20
maze = Maze(maze_with, maze_height)
algorithms[selected_algorithm](maze)
os.environ['SDL_VIDEO_CENTERED'] = '1'
pgzrun.go()