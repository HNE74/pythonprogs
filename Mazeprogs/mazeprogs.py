import pgzrun
import os


# A Maze Cell   
class MazeCell: 

    #constructor method
    def __init__(self, i, w, h):
        self.i = i
        self.w = w
        self.h = h
        self.x = i % w
        self.y = i // w
        self.visited = False
        self.walls = [True, True, True, True]
        self.neighbors = []   

    #draw the cell
    def draw(self, screen, xoffset, yoffset):
        x = self.x * self.w + xoffset
        y = self.y * self.h + yoffset

        if self.walls[0]:
            screen.draw.line((x, y), (x + self.w, y), color="white")
        if self.walls[1]:
            screen.draw.line((x + self.w, y), (x + self.w, y + self.h), color="white")
        if self.walls[2]:
            screen.draw.line((x + self.w, y + self.h), (x, y + self.h), color="white")
        if self.walls[3]:
            screen.draw.line((x, y + self.h), (x, y), color="white") 

# The Maze
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
    
    # Draw the maze
    def draw(self, screen, xoffset, yoffset):
        for cell in self.cells:
            cell.draw(screen, xoffset, yoffset)

def update():
    # Your game logic here
    pass

def draw():
    screen.clear()
    maze = Maze(20, 20)
    maze.draw(screen,50,50) 

def on_key_down(key):
    if key == keys.ESCAPE:  # You can change this to any key you want
        exit()

os.environ['SDL_VIDEO_CENTERED'] = '1'
pgzrun.go()