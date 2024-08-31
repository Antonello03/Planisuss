import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Circle
from world import *
from planisuss_constants import *
from PIL import Image
from scipy.ndimage import gaussian_filter
from creatures import *
import random
from matplotlib.gridspec import GridSpec


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
        self.fig_map = plt.figure(figsize=(10,10))
        self.gs_map = GridSpec(2, 1, height_ratios=[8, 1], figure=self.fig_map)
        
        self.ax_plot = self.fig_map.add_subplot(self.gs_map[0, 0])
        self.ax_plot.set_aspect('equal', adjustable='box')
        self.ax_plot.axis('off')
        self.fig_map.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.fig_map.canvas.manager.set_window_title("Planisuss World")
        
        self. gs_controls = GridSpec(1, 3, figure=self.fig_map, height_ratios=[1], width_ratios=[1, 1, 1], left=0.1, right=0.9, top=0.15, bottom=0.07, wspace=0.05)
        self.ax_pause = self.fig_map.add_subplot(self.gs_controls[0, 0])
        self.ax_play = self.fig_map.add_subplot(self.gs_controls[0, 1])
        self.ax_x2 = self.fig_map.add_subplot(self.gs_controls[0, 2])

        # try:
            # erbast_img = Image.open("C://Users//stefa//OneDrive - Università di Pavia//Downloads//erbastN.jpg")
            # self.erbast_img = erbast_img.resize((10, 10))
            # self.erbast_offset = OffsetImage(np.array(self.erbast_img), zoom=0.5)
        # except FileNotFoundError:
        #     print('The file was not found')
        #     self.carviz_img = None
        self.animal_artists = []
        self.info_box = None
        self.expand = False

        self.anim_running = False
        self.ani = None
        self.fig_map.canvas.mpl_connect('button_press_event', self.onclick)

    def update(self, frameNum, img):
        """Update the grid for animation."""
        # newGrid = env.updateEnv()
        # img.set_data(newGrid)

        for artist in self.animal_artists:
            artist.remove()
        self.animal_artists.clear()

        grid = self.env.getGrid() # I moved this so the method is called only once - Nello
        for i in range(self.grid.shape[0]):
            for j in range(self.grid.shape[1]):
                cell = grid[i, j]
                # print(cell)
                if isinstance(cell, LandCell):
                    for _ in range(2):
                        # offset_image = OffsetImage(self.erbast_img, zoom=0.2)
                        shift_x = np.random.uniform(-0.1, 0.1)
                        shift_y = np.random.uniform(-0.1, 0.1)
                        color = [216 / 255, 158 / 255, 146 / 255]
                        point = Circle((j + shift_x, i + shift_y), radius=0.1, color=color, alpha=1)
                        self.ax_plot.add_artist(point)
                        self.animal_artists.append(point)
                    cell_density = cell.getVegetobDensity()
                    if random.random() > 0.3:
                        cell_density += 10
                    elif random.random() > 0.6:
                        cell_density = cell_density
                    else:
                        cell_density -= 10
                    # print(cell_density)          
                    green_intensity = int((cell_density / 100) * 255) / 255
                    color_vegetob = (0, green_intensity, 0)
                    rectangle = plt.Rectangle((j - 0.5, i - 0.5), 1, 1, color=color_vegetob, alpha=0.4)
                    self.ax_plot.add_artist(rectangle)
                    self.animal_artists.append(rectangle)
    
        return [img] + self.animal_artists

    def onclick(self, event):
        if event.inaxes not in [self.ax_pause, self.ax_play, self.ax_x2]: return
        
        x, y = int(event.xdata), int(event.ydata)
        
        if event.inaxes == self.ax_play:
            print('Play clicked')
            self.start()
        else:
            print('Stop clicked')
            self.pause_animation()


    def gridToRGB(self, grid):
        """ This method translates the environment grid to an RGB matric for visualization"""
        # in future this will be way more complex
        grid_rgb = np.zeros((grid.shape[0], grid.shape[1], 3), dtype=np.uint8)
        get_type = np.vectorize(lambda cell: cell.getCellType()) # Tipo di cella
        cell_types = get_type(grid)
        base_color_land = [139, 69, 19]
        base_color_water = [65, 105, 225]
        grid_rgb[cell_types == 'land'] = base_color_land
        grid_rgb[cell_types == "water"] = base_color_water

        land_mask = (cell_types == 'land')
        water_mask = (cell_types == 'water')
        gradient_land = np.zeros((grid.shape[0], grid.shape[1]), dtype=np.float32)
        gradient_water = np.zeros((grid.shape[0], grid.shape[1]), dtype=np.float32)
        gradient_land[land_mask] = 1.0
        gradient_water[water_mask] = 1.0

        smooth_gradient_land = gaussian_filter(gradient_land, sigma=1.5)
        smooth_color_land = base_color_land * smooth_gradient_land[..., np.newaxis]
        grid_rgb[land_mask] = np.clip(smooth_color_land[land_mask], 0, 255).astype(np.uint8)

        smooth_gradient_water = gaussian_filter(gradient_water, sigma=1.5)
        smooth_color_water = base_color_water * smooth_gradient_water[..., np.newaxis]
        grid_rgb[water_mask] = np.clip(smooth_color_water[water_mask], 0, 255).astype(np.uint8)
        
        return grid_rgb

    def start(self):

        # this is just to see how it would appear, The final mechanism will be more complex I think
        # colors = [(0.0, "blue"), (1.0, "green")]
        # cmap_name = "blue_to_brown"
        # custom_cmap = LinearSegmentedColormap.from_list(cmap_name, colors)

        # print("Grid RGB dtype:", self.grid.dtype)
        # print(f"Grid shape {self.grid.shape}")
        # print(self.grid)

        self.anim_running = True
        self.img = self.ax_plot.imshow(self.grid, interpolation='nearest')

        # print(f"Grid shape: {self.grid.shape}")
        # print(f"Grid contents:\n{self.grid}")

        ani = FuncAnimation(self.fig_map, self.update, fargs=(self.img,),
                             interval=1,
                             blit=True,
                             save_count=10)
        self.ani = ani
        plt.show()

    def pause_animation(self):
        if self.anim_running:
            self.ani.event_source.stop()
            self.anim_running = False
        else:
            self.ani.event_source.start()
            self.anim_running = True


