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
        self.grids = np.array(env.getGrid())
        self.grid = self.gridToRGB(env.getGrid())
        self.img = None
        self.fig_map = plt.figure(figsize=(10,10))
        self.gs_map = GridSpec(2, 2, height_ratios=[6, 1], width_ratios=[6, 1], figure=self.fig_map)
        
        self.ax_plot = self.fig_map.add_subplot(self.gs_map[0, 0])
        self.ax_plot.set_aspect('equal', adjustable='box')
        self.ax_plot.axis('off')
        self.welcome_plot= self.fig_map.add_subplot(self.gs_map[0, 1])
        self.welcome_plot.text(-0.1, 0.5, f'Welcome to Planisuss\nClick on any cell to know more information', va='center')
        self.welcome_plot.axis('off')
        self.fig_map.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05, wspace=0.3, hspace=0.2)
        self.fig_map.tight_layout(pad=1.0)
        self.fig_map.canvas.manager.set_window_title("Planisuss World")
        self.setup_controls()
        
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

    # def start_menu(self):
    #     fig_menu = plt.figure(figsize=(10,10))
    #     gs_menu = GridSpec(1, 3, figure=self.fig_map, height_ratios=[1], width_ratios=[1, 1, 1], left=0.1, right=0.1, top=0.15, bottom=0.07, wspace=0.05)
    #     rgb_maps = map(self.gridToRGB, self.grids)
        
    #     for map in rgb_maps:



    def setup_controls(self):
        gs_controls = GridSpec(1, 3, figure=self.fig_map, height_ratios=[1], width_ratios=[1, 1, 1], left=0.1, right=0.9, top=0.15, bottom=0.07, wspace=0.05)
        controls = {
            'ax_pause' : (self.fig_map.add_subplot(gs_controls[0, 0]), "files//pause.png"),
            'ax_play' : (self.fig_map.add_subplot(gs_controls[0, 1]), "files//play.png"),
            'ax_x2' : (self.fig_map.add_subplot(gs_controls[0, 2]), "files//x2.png")
        
        }
        for name, (ax, pathImg) in controls.items():   
            try:
                img = Image.open(pathImg)
                ax.imshow(img, extent=[0, 1, 0, 1])
                ax.axis('off')
                setattr(self, name, ax)
            except FileNotFoundError:
                print('The image was not found')
                img = None
                setattr(self, name, None)
        self.fig_map.show


    def update(self, frameNum, img):
        """Update the grid for animation."""
        if self.currentDay > self.maxDay:
            self.ani.event_source.stop()
            return [img]
        

        img.set_data(self.grid)
        self.env.nextDay()
        self.day_text.set_text(f"Day: {self.currentDay}")
        
        print(f"{frameNum} and {self.currentDay}")
        # newGrid = self.env.getGrid()
        # rgbGrid = self.gridToRGB(newGrid)

        # img.set_data(self.grid)

        for artist in self.animal_artists:
            artist.remove()
        self.animal_artists.clear()

        if not self.animal_artists:
           self.draw_elements(self.grid)
        else:
            print("The artist list should be cleared")
        
        self.currentDay += 1
    
        return [img, self.day_text] + self.animal_artists
    
    def draw_elements2(self):
        # getting the total number of erbasts and 
        pass
    
    def draw_elements(self, grid):
        for i in range(grid.shape[0]):
            for j in range(grid.shape[1]):
                cell = self.env.getGrid()[i, j]
                
                if isinstance(cell, LandCell):
                    erbast_list = cell.getErbastList()
                    carviz_list = cell.getCarvizList()
                    if erbast_list or carviz_list:
                        for erbast in erbast_list:
                            # print(f"cell: {i, j}")
                            self.draw_animal(erbast)
                        for carviz in carviz_list:
                            self.draw_animal(carviz)   
                    
                    self.draw_vegetob(cell, i, j)
    
    def draw_animal(self, animal):
        shift_x = np.random.uniform(-0.3, 0.3)
        shift_y = np.random.uniform(-0.3, 0.3)
        x, y = animal.getCoords()
        # print('coordinates', (x, y))
        if isinstance(animal, Erbast):
            color = [216 / 255, 158 / 255, 146 / 255]
        else:
            color = [139 / 255, 0 / 255, 0 / 255]
        point = Circle((y + shift_y, x + shift_x), radius=0.1, color=color, alpha=1)
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
        if event.inaxes not in [self.ax_pause, self.ax_play, self.ax_x2, self.ax_plot]: return
        
        x, y = event.xdata, event.ydata
        print(self.grid.shape)
        grid_height, grid_width = self.grid.shape[0], self.grid.shape[1]
        cell_width = (self.ax_plot.get_xlim()[1] - self.ax_plot.get_xlim()[0]) / grid_width
        cell_height = (self.ax_plot.get_ylim()[0] - self.ax_plot.get_ylim()[1]) / grid_height
        grid_x = int((y - self.ax_plot.get_ylim()[1]) // cell_height)
        grid_y = int((x - self.ax_plot.get_xlim()[0]) // cell_width)
        
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
        elif event.inaxes == self.ax_plot:
            if self.anim_running:
                self.pause_animation()
            # self.env.nextDay()
            print(f"cell {grid_x,grid_y} has been clicked")
            self.show_cell_info(grid_x, grid_y)
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
                                interval=2000,
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
            self.ani.event_source.interval = 50
            self.ani.event_source.start()
            self.faster = True
    
    def normal_animation(self):
        if self.faster:
            self.ani.event_source.stop()
            self.ani.event_source.interval = 2000
            self.ani.event_source.start()
            self.faster = False

    def show_cell_info(self, x, y):
        cell = self.env.getGrid()[x, y]
        fig = plt.figure(figsize=(5,5))
        gs = GridSpec(2, 2, height_ratios=[3, 1], figure=fig)
        ax_img = fig.add_subplot(gs[0, 0])
        test2 = Image.open("files//carvizN.jpg")
        # ax = ShowCard.remove_text(self.ax[1])
        extent = [0, 0.5, 0.5, 1]
        ax_img.imshow(test2, extent=extent)
        ax_img.text(0.01, 0.45, f"Cell's coordinates: {x}, {y}", ha='left')
        ax_img.text(0.01, 0.35, f"Cell's vegetob density: {cell.getVegetobDensity()}")
        ax_img.axis('off')
        
        
        erbast_list = cell.getErbastList()
        carviz_list = cell.getCarvizList()
        if erbast_list:
            tot_erbast = len(erbast_list)
            erbast_empty = False
        else:
            print("There are no erbasts in the cell")
            tot_erbast =  1
            erbast_empty = True
        if carviz_list:
            tot_carviz = len(carviz_list)
            carviz_empty = False
        else:
            print("There are no carviz in the cell")
            tot_carviz = 1
            carviz_empty = True
        print(f"Amount of erbasts in cell {x, y}= {erbast_list} sum {tot_erbast}")
        print(f"Amount of erbasts in cell {x, y}= {carviz_list} sum {tot_carviz}")
        total_rows = tot_erbast + tot_carviz + 2
        height_ratios = [0.1 for _ in range(total_rows)]
        gs_animals = GridSpec(total_rows, 1, figure=fig, height_ratios=height_ratios, width_ratios=[0.1], left=0.7, right=0.95, top=0.9, bottom=0.1) 
        
        axis_erbast = self.axis_individuals(tot_erbast, fig, gs_animals, 0, erbast=True, list_animals= erbast_list, empty=erbast_empty)
        axis_carviz = self.axis_individuals(tot_carviz, fig, gs_animals, tot_erbast+1, erbast=False, list_animals = carviz_list, empty=carviz_empty)   
        
        print("erbast axis", axis_erbast)
        print("carviz axis", axis_carviz)

        self.individuals_axis = axis_erbast + axis_carviz

        fig.canvas.draw()
        fig.show()

        fig.canvas.mpl_connect('button_press_event', lambda event: self.track_onclick(event, self.individuals_axis))
    
    def axis_individuals(self, n : int, fig, gs, start_row, erbast : bool, list_animals : list, empty : bool):
        title_pos = start_row
        ax_title = fig.add_subplot(gs[title_pos, 0])
        t = f"Erbast in cell" if erbast else f"Carviz in cell"
        ax_title.text(0.3, 0.3, t, ha='center')
        ax_title.axis('off')

        s = 'Erbast' if erbast else 'Carviz'
        s_empty = 'There are no Erbast in cell' if empty and erbast else 'There is no Carviz in cell'
        individuals_axis = []
        for i in range(n):
            ax = fig.add_subplot(gs[start_row + 1 + i, 0])
            if empty:
                ax.text(0.3, 0.3, f"{s_empty}", ha='center', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round'))
                individuals_axis.append((ax, None))
            else:
                ax.text(0.3, 0.3, f"{s+str(i+1)}", ha='center', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round'))
                individuals_axis.append((ax, list_animals[i]))

            ax.axis('off')

        fig.canvas.draw()
        return individuals_axis
    
    def track_onclick(self, event, individuals_axis):
        for i, (ax, individual) in enumerate(individuals_axis):
            if ax == event.inaxes:
                self.show_individuals(individual)
                break

    def show_individuals(self, clicked_individual):
        fig = plt.figure(figsize=(5,5))
        gs_stats = GridSpec(5, 2, figure=fig, width_ratios=[1, 1], height_ratios=[0.4, 0.4, 0.4, 0.2, 0.2], left=0.05, right=0.95, top=0.9, bottom=0.1)

        # Adding the pixel art on the left
        ax_animal = fig.add_subplot(gs_stats[0:2, 0])  # Span over multiple rows for the pixel art
        animal_path = "files//carvizN.jpg" if isinstance(clicked_individual, Carviz) else "files//erbastN.jpg"
        animal_art = Image.open(animal_path)
        ax_animal.imshow(animal_art, extent=[0.0, 1.0, 0.0, 1.0])
        ax_animal.text(0.5, -0.1, f"Individual's ID: {clicked_individual.ID} ", fontsize=8, ha='center', va='center', transform=ax_animal.transAxes)
        ax_animal.axis('off')

        # First row (energy bar) on the right
        individual_energy = clicked_individual.getEnergy()
        if individual_energy < 30:
            energy_path = "files//energy1.png"
        elif 30 <= individual_energy < 100:
            energy_path = "files//energy2.png"
        elif individual_energy == 100:
            energy_path = "files//energy3.png"
        ax_energy = fig.add_subplot(gs_stats[0, 1])
        energy = Image.open(energy_path).resize((2000, 700))
        ax_energy.imshow(energy)
        ax_energy.text(0.5, -0.1, f'Energy: {individual_energy}', fontsize=8, ha='left', va='center', transform=ax_energy.transAxes)
        ax_energy.axis('off')

        # Second row (strength bar)
        individual_age = clicked_individual.age
        ax_age = fig.add_subplot(gs_stats[1, 1])
        heart = Image.open("files//heart_png.png")
        ax_age.imshow(heart)
        ax_age.text(1.0, 0.5, f'Age: {individual_age}', fontsize=8, ha='left', va='center', transform=ax_age.transAxes)
        ax_age.axis('off')

        # Third row (social attention bar)
        individual_att = clicked_individual.socialAttitude
        if individual_att < 0.3:
            att_path = "files//SocAtt1.png"
        elif 0.3 <= individual_att < 1:
            att_path = "files//SocAtt2.png"
        elif individual_att == 1:
            att_path = "files//SocAtt3.png"
        ax_social_att = fig.add_subplot(gs_stats[2, 1])
        socialAtt = Image.open(att_path).resize((2000, 700))
        ax_social_att.imshow(socialAtt)
        ax_social_att.text(0.5, -0.1, f'Social ATT: {individual_att}', fontsize=8, ha='left', va='center', transform=ax_social_att.transAxes)
        ax_social_att.axis('off')

        # Coordinates (at the bottom left)
        ax_coords = fig.add_subplot(gs_stats[3, 0])
        ax_coords.text(0.5, 0.5, f'Coords: {clicked_individual.coords}', fontsize=8, ha='center', va='center', transform=ax_coords.transAxes)
        ax_coords.axis('off')

        # Extra info at the bottom right
        ax_info = fig.add_subplot(gs_stats[3, 1])
        ax_info.text(0.5, 0.5, 'Extra Info:', fontsize=8, ha='center', va='center', transform=ax_info.transAxes)
        social_group = "Individual belongs to a social group" if clicked_individual.inSocialGroup else "Individual is alone"
        ax_info.text(0.5, 0.15, social_group, fontsize=8, ha='center', va='center', transform=ax_info.transAxes)
        ax_info.axis('off')

        fig.subplots_adjust(hspace=0.7)
        fig.show()



