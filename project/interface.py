import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Circle, BoxStyle, Rectangle
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
    IMAGE_PATHS = {
        'SOCIAL_ATT': {
            'LOW': "files//SocAtt1.png",
            'MEDIUM': "files//SocAtt2.png",
            'HIGH': "files//SocAtt3.png"
        },
        'ENERGY': {
            'LOW': "files//energy1.png",
            'MEDIUM': "files//energy2.png",
            'HIGH': "files//energy3.png"
        }
    }
    COLORS = (234/255, 222/255, 204/255, 0.7)


    def __init__(self, env):
        
        if not isinstance(env, Environment):
            raise TypeError(f"Expected env to be an instance of Environment, but got {type(env).__name__} instead.")
        
        self.initialize_attributes(env)
        self.fig_map
        self.fig_map.canvas.mpl_connect('button_press_event', self.onclick)
        self.day_text = self.ax_plot.text(0.02, 0.95, f'Day 0', bbox={'facecolor':'w', 'alpha':0.5}, transform=self.ax_plot.transAxes)

    def initialize_attributes(self, env):
        self.env = env
        self.grid = self.gridToRGB(env.getGrid())
        self.img = None
        self.currentDay = 0
        self.maxDay = NUMDAYS
        self.animal_artists_map = {}
        self.vegetob_artists = []
        self.processed_dead_animals = set()
        self.info_box = None
        self.expand = False
        self.anim_running = False
        self.ani = None
        self.faster = False
        self.selected_map = None

    def start_menu(self):
        plt.ion()
        fig_menu = plt.figure(figsize=(10,10))
        gs_menu = GridSpec(2, 3, figure=fig_menu, height_ratios=[1, 3], width_ratios=[1, 1, 1], left=0.1, right=0.9, top=0.9, bottom=0.1, wspace=0.05, hspace=0.3)
        ax_title = fig_menu.add_subplot(gs_menu[0, 1])
        ax_title.set_title("Image Title")
        ax_title.axis('off')

        ax_map1 = fig_menu.add_subplot(gs_menu[1, 0])
        ax_map2 = fig_menu.add_subplot(gs_menu[1, 1])
        ax_map3 = fig_menu.add_subplot(gs_menu[1, 2])
        
        fig_menu.canvas.mpl_connect('button_press_event', lambda event: self.choose_map(fig_menu, event))
        fig_menu.show()
    
    def choose_map(self, fig_menu, event):
        if event.inaxes not in fig_menu.get_axes(): return

        title, map1, map2, map3 = list(fig_menu.get_axes())
        
        if event.inaxes == title:
            print('Title clicked')
        elif event.inaxes == map1:
            print("map1 clicked")
        elif event.inaxes == map2:
            print("map2 clicked")
        elif event.inaxes == map3:
            print("map3 clicked")

    @property
    def fig_map(self):
        if not hasattr(self, '_fig_map'):
            self._fig_map = plt.figure(figsize=(7, 7))
            self._fig_map.set_facecolor(self.COLORS)
            self.gs_map = GridSpec(2, 2, height_ratios=[6, 1], width_ratios=[6, 1], figure=self._fig_map)
            
            self.ax_plot = self._fig_map.add_subplot(self.gs_map[0, 0])
            self.ax_plot.set_aspect('equal', adjustable='box')
            self.ax_plot.axis('off')
            self.welcome_plot = self._fig_map.add_subplot(self.gs_map[0, 1])
            self.welcome_plot.text(-0.1, 0.5, f'Click on any cell to know more information', va='center')
            self.welcome_plot.axis('off')
            self._fig_map.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05, wspace=0.3, hspace=0.2)
            self._fig_map.tight_layout(pad=1.0)
            self._fig_map.canvas.manager.set_window_title("Planisuss World")
            self.setup_controls()
        return self._fig_map


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
        
        self.currentDay = frameNum
        
        if self.currentDay >= self.maxDay:
            self.ani.event_source.stop()
            return [img]
        
        self.env.nextDay()
        img = self.ax_plot.imshow(self.grid, interpolation='nearest')
        print(f"{frameNum} and {self.currentDay}")
        self.day_text.set_text(f"Day: {self.currentDay}")
        
        for artist in self.vegetob_artists:
            artist.remove()
        self.vegetob_artists.clear()

        self.draw_elements(self.grid)
        
        return [img, self.day_text] + list(self.animal_artists_map.values()) + self.vegetob_artists
    
    def draw_elements(self, grid):
        for i in range(grid.shape[0]):
            for j in range(grid.shape[1]):
                cell = self.env.getGrid()[i, j]
                if isinstance(cell, LandCell):
                    self.draw_animals_in_cell(cell)
                    self.draw_vegetob(cell, i, j)

    def draw_animals_in_cell(self, cell):
        erbast_list = cell.getErbastList()
        carviz_list = cell.getCarvizList()
        dead_list = cell.getDeadCreaturesList()

        already_seen = set()
        
        for animal in erbast_list + carviz_list:
            already_seen.add(animal)
            redraw = animal in dead_list
            self.draw_animal(animal, redraw=redraw)

        if dead_list:
            print("There are dead animals")
            print(len(dead_list))
            for dead in dead_list:
                if dead not in already_seen and dead not in self.processed_dead_animals:
                    self.draw_animal(dead, redraw=True)
                    self.processed_dead_animals.add(dead)

    def draw_animal(self, animal, redraw=False):
        
        shift_x, shift_y = np.random.uniform(-0.3, 0.3, 2)
        x, y = animal.getCoords()        

        if animal in self.animal_artists_map:
            current_artist = self.animal_artists_map[animal]
            if redraw:
                print(f"animal is now dead")
                current_artist.remove()
                del self.animal_artists_map[animal]
                print(animal)
                color = [192 / 255, 192 / 255, 192 / 255]
                new_artist = Rectangle(xy=(y + shift_y, x + shift_x), width=0.2, height=0.2, color=color, fill=True, alpha=1)
                self.ax_plot.add_artist(new_artist)
                self.animal_artists_map[animal] = new_artist
                self.processed_dead_animals.add(animal)  # Mark as processed
            else:
                if isinstance(current_artist, Circle):
                    current_artist.center = (y + shift_y, x + shift_x)
                return current_artist    
        else:
            print("Animal not in map")
            if redraw:
                print(f"animal is dead and was not in map")
                print(animal)
                color = [192 / 255, 192 / 255, 192 / 255]
                new_artist = Rectangle(xy=(y + shift_y, x + shift_x), width=0.2, height=0.2, color=color, fill=True, alpha=1)
                self.ax_plot.add_artist(new_artist)
                self.animal_artists_map[animal] = new_artist
                self.processed_dead_animals.add(animal)  # Mark as processed
            else:
                if isinstance(animal, Erbast):
                    color = [216 / 255, 158 / 255, 146 / 255]
                else:
                    color = [139 / 255, 0 / 255, 0 / 255]
                new_artist = Circle((y + shift_y, x + shift_x), radius=0.1, color=color, alpha=1)
                self.animal_artists_map[animal] = new_artist
                self.ax_plot.add_artist(new_artist)        
        
    def draw_vegetob(self, cell, i, j):
        cell_density = cell.getVegetobDensity()
        # print(f"cell density: {cell_density}")          
        green_intensity = int((cell_density / MAX_GROWTH) * 255) / 255
        color_vegetob = (0, green_intensity, 0)
        rectangle = plt.Rectangle((j - 0.5, i - 0.5), 1, 1, color=color_vegetob, alpha=0.4)
        self.ax_plot.add_artist(rectangle)
        self.vegetob_artists.append(rectangle)
        
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
            if self.currentDay == 0:
                self.img = self.display_initial_setup()
                plt.pause(1)
            # self.img = self.ax_plot.imshow(self.grid, interpolation='nearest')
            self.ani = FuncAnimation(self.fig_map, self.update, frames=list(range(1, self.maxDay + 1)), fargs=(self.img,),
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

        for artist in self.animal_artists_map.values():
            artist.remove()
        
        self.animal_artists_map.clear()
        # self.animal_artists.clear()

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
        dead_list = cell.getDeadCreaturesList()
        if dead_list:
            print("There are dead animals in the cell")
            tot_dead = len(dead_list)
            dead_empty = False
        else:
            print("There are no dead animals in the cell")
            tot_dead = 1
            dead_empty = True
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
        total_rows = tot_erbast + tot_carviz + tot_dead + 3
        height_ratios = [0.1 for _ in range(total_rows)]
        gs_animals = GridSpec(total_rows, 1, figure=fig, height_ratios=height_ratios, width_ratios=[0.1], left=0.7, right=0.95, top=0.9, bottom=0.1) 
        
        axis_erbast = self.axis_individuals(tot_erbast, fig, gs_animals, 0, erbast=True, carviz=False, list_animals= erbast_list, empty=erbast_empty)
        axis_carviz = self.axis_individuals(tot_carviz, fig, gs_animals, tot_erbast+1, erbast=False, carviz=True, list_animals = carviz_list, empty=carviz_empty)
        axis_dead = self.axis_individuals(tot_dead, fig, gs_animals, tot_erbast+tot_carviz+2, erbast=False, carviz=False, list_animals = dead_list, empty=dead_empty)   
        
        print("erbast axis", axis_erbast)
        print("carviz axis", axis_carviz)

        self.individuals_axis = axis_erbast + axis_carviz + axis_dead

        fig.canvas.draw()
        fig.show()

        fig.canvas.mpl_connect('button_press_event', lambda event: self.track_onclick(event, self.individuals_axis))
    
    def axis_individuals(self, n : int, fig, gs, start_row, erbast : bool, carviz : bool, list_animals : list, empty : bool):
        title_pos = start_row
        ax_title = fig.add_subplot(gs[title_pos, 0])
        if erbast:
            t = f"Erbast in cell"
        elif carviz:
            t = f"Carviz in cell"
        else:
            t = f"Dead animals in cell"
        ax_title.text(0.3, 0.3, t, ha='center')
        ax_title.axis('off')
        
        s_empty = 'There are no Erbast in cell' if empty and erbast else 'There is no Carviz in cell'
        individuals_axis = []
        for i in range(n):
            ax = fig.add_subplot(gs[start_row + 1 + i, 0])
            if empty:
                ax.text(0.3, 0.3, f"{s_empty}", ha='center', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round'))
                individuals_axis.append((ax, None))
            else:
                animal = list_animals[i]
                if isinstance(animal, Erbast):
                    s = f"Erbast{str(animal.id)}"
                elif isinstance(animal, Carviz):
                    s = f"Carviz{str(animal.id)}"
                else:
                    s = f"Dead animal {str(animal.old_species)}{str(animal.id)}"
                ax.text(0.3, 0.3, f"{s}", ha='center', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round'))
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
        """Display individual's information in a new figure."""
        fig = plt.figure(figsize=(5,5))
        gs_stats = GridSpec(5, 2, figure=fig, 
                        width_ratios=[1, 1], 
                        height_ratios=[0.4, 0.4, 0.4, 0.2, 0.2], 
                        left=0.05, right=0.95, top=0.9, bottom=0.1)
        
        # Create subplots
        if isinstance(clicked_individual, DeadCreature):
            clicked_individual = clicked_individual.deadAnimal
        self.create_animal_subplot(fig, gs_stats, clicked_individual)
        self.create_age_subplot(fig, gs_stats, clicked_individual.age)
        self.create_energy_subplot(fig, gs_stats, clicked_individual.getEnergy())
        self.create_social_att_subplot(fig, gs_stats, clicked_individual.socialAttitude)
        
        # Additional info
        ax_coords = fig.add_subplot(gs_stats[3, 0])
        ax_coords.text(0.5, 0.5, f'Coords: {clicked_individual.coords}', 
                    fontsize=8, ha='center', va='center', transform=ax_coords.transAxes)
        ax_coords.axis('off')
        
        ax_info = fig.add_subplot(gs_stats[3, 1])
        ax_info.text(0.5, 0.5, 'Extra Info:', 
                    fontsize=8, ha='center', va='center', transform=ax_info.transAxes)
        social_group = "Individual belongs to a social group" if clicked_individual.inSocialGroup else "Individual is alone"
        ax_info.text(0.5, 0.15, social_group, 
                    fontsize=8, ha='center', va='center', transform=ax_info.transAxes)
        status = "Alive" if clicked_individual.alive else "Dead"
        ax_info.text(0.5, -0.2, f"Status: {status}", 
                    fontsize=8, ha='center', va='center', transform=ax_info.transAxes)
        ax_info.axis('off')
        
        fig.subplots_adjust(hspace=0.7)
        fig.show()

    def create_animal_subplot(self, fig, gs_stats, clicked_individual):
        """Create subplot for animal image."""
        ax_animal = fig.add_subplot(gs_stats[0:2, 0])
        animal_path = "files//carvizN.jpg" if isinstance(clicked_individual, Carviz) else "files//erbastN.jpg"
        animal_art = Image.open(animal_path)
        ax_animal.imshow(animal_art, extent=[0.0, 1.0, 0.0, 1.0])
        ax_animal.text(0.5, -0.1, f"Individual's ID: {clicked_individual.id} ", 
                    fontsize=8, ha='center', va='center', transform=ax_animal.transAxes)
        ax_animal.axis('off')
        return ax_animal
    
    def create_age_subplot(self, fig, gs_stats, individual_age):
        ax_age = fig.add_subplot(gs_stats[1, 1])
        heart = Image.open("files//heart_png.png")
        ax_age.imshow(heart)
        ax_age.text(1.0, 0.5, f'Age: {individual_age}', fontsize=8, ha='left', va='center', transform=ax_age.transAxes)
        ax_age.axis('off')
        return ax_age

    def create_social_att_subplot(self, fig, gs_stats, individual_att):
        att_path = self._get_social_att_image(individual_att)
        ax_social_att = fig.add_subplot(gs_stats[2, 1])
        socialAtt = Image.open(att_path).resize((2000, 700))
        ax_social_att.imshow(socialAtt)
        ax_social_att.text(0.5, -0.1, f'Social ATT: {individual_att}', fontsize=8, ha='left', va='center', transform=ax_social_att.transAxes)
        ax_social_att.axis('off')
        return ax_social_att
    
    def _get_social_att_image(self, attitude):
        """
        Return appropriate image path based on social attribute value.
        
        Args:
            social attribute (int): Social Attribute level of the individual
            
        Returns:
            str: Path to the appropriate social attribute image
        """
        if attitude < 30:
            return self.IMAGE_PATHS['SOCIAL_ATT']['LOW']
        elif attitude < 100:
            return self.IMAGE_PATHS['SOCIAL_ATT']['MEDIUM']
        return self.IMAGE_PATHS['SOCIAL_ATT']['HIGH']
    

    def create_energy_subplot(self, fig, gs_stats, individual_energy):
        """
        Create subplot showing energy level with appropriate image.
        
        Args:
            fig: matplotlib figure
            gs_stats: GridSpec object
            individual_energy (float): Energy level of the individual
        """
        energy_path = self._get_energy_image(individual_energy)
        ax_energy = fig.add_subplot(gs_stats[0, 1])
        energy = Image.open(energy_path).resize((2000, 700))
        ax_energy.imshow(energy)
        ax_energy.text(0.5, -0.1, f'Energy: {individual_energy}', 
                    fontsize=8, ha='left', va='center', 
                    transform=ax_energy.transAxes)
        ax_energy.axis('off')
        return ax_energy

    def _get_energy_image(self, energy):
        """
        Return appropriate image path based on energy value.
        
        Args:
            energy (float): Energy level of the individual
            
        Returns:
            str: Path to the appropriate energy image
        """
        if energy < 30:
            return self.IMAGE_PATHS['ENERGY']['LOW']
        elif energy < 100:
            return self.IMAGE_PATHS['ENERGY']['MEDIUM']
        return self.IMAGE_PATHS['ENERGY']['HIGH']


    def run_simulation(self):
        # self.start_menu()
        self.start()
        plt.show()



