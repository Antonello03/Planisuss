import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from world import Environment
from planisuss_constants import *

env = Environment()

ON = 255
OFF = 0

def update(frameNum, img):
    """Update the grid for animation."""
    newGrid = env.updateEnv()
    img.set_data(newGrid)
    return img,

grid = env.getEnv()

# Create the plot
fig, ax = plt.subplots()
img = ax.imshow(grid, interpolation='nearest', cmap='gray')
ani = FuncAnimation(fig, update, fargs=(img,),
                    interval=1,
                    save_count=50)

plt.show()
