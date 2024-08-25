import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import LinearSegmentedColormap
from world import Environment
from planisuss_constants import *


class Interface():

    """
    Class that handles the visualization of the interface
    Maybe we can put even the following in a class?
    """

    def __init__(self, env):

        if not isinstance(env, Environment):
            raise TypeError(f"Expected env to be an instance of Environment, but got {type(env).__name__} instead.")
        
        self.env = env
        self.grid = self.gridToRGB(env.getGrid())
        self.fig, self.ax = plt.subplots(figsize=(5, 5))

        # better window appearance
        self.ax.axis('off')
        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.fig.canvas.manager.set_window_title("Planisuss World")

    def update(self, frameNum, img):
        """Update the grid for animation."""
        #newGrid = env.updateEnv()
        #img.set_data(newGrid)
        return img,

    def gridToRGB(self, grid):
        """ This method translates the environment grid to an RGB matric for visualization"""
        # in future this will be way more complex
        get_type = np.vectorize(lambda cell: cell.getCellType())
        grid = np.where(get_type(grid) == "land", 255, 0)
        return grid

    def start(self):

        # this is just to see how it would appear, The final mechanism will be more complex I think
        colors = [(0.0, "blue"), (1.0, "green")]
        cmap_name = "blue_to_brown"
        custom_cmap = LinearSegmentedColormap.from_list(cmap_name, colors)

        self.img = self.ax.imshow(self.grid, interpolation='nearest', cmap = custom_cmap)

        ani = FuncAnimation(self.fig, self.update, fargs=(self.img,),
                            interval=1,
                            save_count=50)
        plt.show()


