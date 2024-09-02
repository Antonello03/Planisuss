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
        self.img = None
        self.fig_map = plt.figure(figsize=(10,10))
        self.gs_map = GridSpec(2, 1, height_ratios=[8, 1], figure=self.fig_map)
        
        self.ax_plot = self.fig_map.add_subplot(self.gs_map[0, 0])
        self.ax_plot.set_aspect('equal', adjustable='box')
        self.ax_plot.axis('off')
        self.fig_map.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.fig_map.canvas.manager.set_window_title("Planisuss World")
        
        self.gs_controls = GridSpec(1, 3, figure=self.fig_map, height_ratios=[1], width_ratios=[1, 1, 1], left=0.1, right=0.9, top=0.15, bottom=0.07, wspace=0.05)
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
        self.currentDay = 0
        self.maxDay = NUMDAYS
        self.day_text = self.ax_plot.text(0.02, 0.95, f'Day 0', bbox={'facecolor':'w', 'alpha':0.5}, transform=self.ax_plot.transAxes)
        self.animal_artists = []
        self.info_box = None
        self.expand = False

        self.anim_running = False
        self.ani = None
        self.faster = False
        self.fig_map.canvas.mpl_connect('button_press_event', self.onclick)

    def update(self, frameNum, img):
        """Update the grid for animation."""
        if self.currentDay > self.maxDay:
            self.ani.event_source.stop()
            return [img]
        
        self.env.nextDay()
        self.day_text.set_text(f"Day: {self.currentDay}")
        
        print(f"{frameNum} and {self.currentDay}")
        # newGrid = self.env.getGrid()
        # rgbGrid = self.gridToRGB(newGrid)

        img.set_data(self.grid)

        for artist in self.animal_artists:
            artist.remove()
        self.animal_artists.clear()

        if not self.animal_artists:
           self.draw_elements(self.grid)
        else:
            print("The artist list should be cleared")
        
        self.currentDay += 1
    
        return [img, self.day_text] + self.animal_artists
    
    def draw_elements(self, grid):
        for i in range(grid.shape[0]):
            for j in range(grid.shape[1]):
                cell = self.env.getGrid()[i, j]  # Assuming env.getGrid() gives the latest grid
                
                if isinstance(cell, LandCell):
                    erbast_list = cell.getErbastList()
                    carviz_list = cell.getCarvizList()
                    
                    # Draw animals
                    for erbast in erbast_list:
                        self.draw_animal(erbast)
                    for carviz in carviz_list:
                        self.draw_animal(carviz)
                    
                    # Draw vegetation or other features
                    self.draw_vegetob(cell, i, j)
    
    def draw_animal(self, animal):
        shift_x = np.random.uniform(-0.3, 0.3)
        shift_y = np.random.uniform(-0.3, 0.3)
        x, y = animal.getCoords()
        print('coordinates', (x, y))
        if isinstance(animal, Erbast):
            color = [216 / 255, 158 / 255, 146 / 255]
        else:
            color = [139 / 255, 0 / 255, 0 / 255]
        point = Circle((x + shift_x, y + shift_y), radius=0.1, color=color, alpha=1)
        self.ax_plot.add_artist(point)
        self.animal_artists.append(point)
    
    def draw_vegetob(self, cell, i, j):
        cell_density = cell.getVegetobDensity()
        # print(f"cell density: {cell_density}")          
        green_intensity = int((cell_density / 100) * 255) / 255
        color_vegetob = (0, green_intensity, 0)
        rectangle = plt.Rectangle((j - 0.5, i - 0.5), 1, 1, color=color_vegetob, alpha=0.4)
        self.ax_plot.add_artist(rectangle)
        self.animal_artists.append(rectangle)
        
    def onclick(self, event):
        if event.inaxes not in [self.ax_pause, self.ax_play, self.ax_x2]: return
        
        x, y = int(event.xdata), int(event.ydata)
        
        if event.inaxes == self.ax_play:
            print('Play clicked')
            if not self.anim_running:
                self.start()
            else:  
                self.pause_animation()
        elif event.inaxes == self.ax_x2:
            print("x2 clicked")
            if self.faster:
                print("Reverting to normal speed")
                self.normal_animation()
            else:
                self.faster_animation()
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

        self.apply_filter(gradient_land, base_color_land, land_mask, grid_rgb)
        self.apply_filter(gradient_water, base_color_water, water_mask, grid_rgb)
        
        return grid_rgb
    
    def apply_filter(self, gradient_arr, base_color, mask, grid_rgb):
        smooth_gradient_land = gaussian_filter(gradient_arr, sigma=1.5)
        smooth_color_land = np.array(base_color) * smooth_gradient_land[..., np.newaxis]
        grid_rgb[mask] = np.clip(smooth_color_land[mask], 0, 255).astype(np.uint8)


    def start(self):
        if self.ani is None:
            self.currentDay = 0
            
            self.img = self.display_initial_setup()
            # self.img = self.ax_plot.imshow(self.grid, interpolation='nearest')
            self.ani = FuncAnimation(self.fig_map, self.update, fargs=(self.img,),
                                interval=1400,
                                blit=False,
                                repeat=False,
                                cache_frame_data=False)
        else:
            self.ani.event_source.start()
        self.anim_running = True
        plt.show()

    def display_initial_setup(self):
        initial_grid = self.grid

        for artist in self.animal_artists:
            artist.remove()
        self.animal_artists.clear()

        self.draw_elements(initial_grid)

        # Update the display to show Day 0
        self.img = self.ax_plot.imshow(initial_grid, interpolation='nearest')
        self.day_text.set_text(f'Day 0')
        # plt.pause(0.1)
        return self.img

    def pause_animation(self):
        if self.anim_running:
            self.ani.event_source.stop()
            self.anim_running = False
        else:
            self.ani.event_source.start()
            self.anim_running = True

    
    def faster_animation(self):
        if self.anim_running:
            self.ani.event_source.stop()
            faster_ani = FuncAnimation(
                self.fig_map, self.update, fargs=(self.img,),
                interval=50, blit=False, repeat=False, cache_frame_data=False)
            self.ani = faster_ani
            self.ani.event_source.start()
            self.faster = True
    
    def normal_animation(self):
        if self.faster:
            self.ani.event_source.stop()
            normal_ani = FuncAnimation(self.fig_map, self.update, fargs=(self.img,),
                             interval=1000,
                             blit=False,
                             repeat=False,
                             cache_frame_data=False)
            self.ani = normal_ani
            self.ani.event_source.start()
            self.faster = False


