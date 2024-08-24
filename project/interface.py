import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import LinearSegmentedColormap

from world import Environment
from planisuss_constants import *

"""
File that handles the visualization of the interface

Maybe we can put even the following in a class?
"""

env = Environment()

ON = 255
OFF = 0

def update(frameNum, img):
    """Update the grid for animation."""
    #newGrid = env.updateEnv()
    #img.set_data(newGrid)
    return img,

grid = env.getGrid()

# Create the plot
fig, ax = plt.subplots(figsize=(5, 5))

# this is just to see how it would appear, The final mechanism will be more complex I think
colors = [(0.0, "blue"), (1.0, "green")]
cmap_name = "blue_to_brown"
custom_cmap = LinearSegmentedColormap.from_list(cmap_name, colors)

img = ax.imshow(grid, interpolation='nearest', cmap = custom_cmap)

# better window appearance
ax.axis('off')
fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
fig.canvas.manager.set_window_title("Planisuss World")

ani = FuncAnimation(fig, update, fargs=(img,),
                    interval=1,
                    save_count=50)

plt.show()