x = 50
y = 50
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = f'{x},{y}'
import pgzrun, random
from pgzhelper import *

WIDTH=800
HEIGHT=600

runner = Actor('run__000')
run_images = ['run__000', 'run__001', 'run__002', 'run__003', 'run__004', 'run__005', 'run__006', 'run__007', 'run__008', 'run__009']
runner.images = run_images


def update():
    runner.fps=1
    runner.animate()

    #runner.next_image()

def draw():
    screen.draw.filled_rect(Rect(0,0,800,400), (163, 232, 254))
    screen.draw.filled_rect(Rect(0,400,800,200), (88, 242, 152))
    runner.draw()

pgzrun.go() # Must be last line

