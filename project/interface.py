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
import logging
import traceback
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='animation_debug.log',
                    filemode='w')
logger = logging.getLogger('Interface')

log_filename = f"run_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
logging.basicConfig(
    filename="planisuss_events.log",
    filemode="w",        
    level=logging.INFO,
    format="%(levelname)s - %(message)s",
)

class Interface():

    """
    Class that handles the visualization of the interface
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
        },
        'CELL': {
            'DIRT' : "files//dirt.png",
            'GRASS_LOW' : "files//grass_low.png",
            'GRASS_MED' : "files//grass_med.png",
            'GRASS_HIGH' : "files//grass_high.png"
        }
    }
    COLORS = (5/255, 8/255, 10/255, 0.7)

    WORLD_CONFIGS = {
    "map1": {"seed": 1},
    "map2": {"seed": 15},
    "map3": {"seed": 44}
    }

    MAP_PATHS = "files//maps"

    def __init__(self):
        
        # if not isinstance(env, Environment):
        #     raise TypeError(f"Expected env to be an instance of Environment, but got {type(env).__name__} instead.")
        
        self.initialize_attributes()
        self._fig_map = None
        # self.fig_map.canvas.mpl_connect('button_press_event', self.onclick)
        # self.day_text = self.ax_plot.text(0.02, 0.95, f'Day 0', bbox={'facecolor':'w', 'alpha':0.5}, transform=self.ax_plot.transAxes)
        self.fig_menu = None

    def initialize_attributes(self):
        self.img = None
        self.currentDay = 0
        self.maxDay = NUMDAYS
        self.alive_animal_artists = {}  
        self.dead_animal_artists = {}   
        self.vegetob_artists = []
        self.processed_dead_animals = set()
        self.info_box = None
        self.expand = False
        self.anim_running = False
        self.ani = None
        self.faster = False
        self.selected_map = None
        self.generation_type = "random"
        self.numErb = 50
        self.numCarv = 50

    def run_simulation(self):
        plt.ion() 
        self.start_menu()
        plt.show(block=True)

    def start_menu(self):
        self.fig_menu = plt.figure(figsize=(8,8), dpi=100)
        self.fig_menu.set_facecolor(self.COLORS)
        
        background_ax = self.fig_menu.add_axes([0, 0, 1, 1])
        background_img = Image.open("files//background.jpg")
        background_ax.imshow(background_img, aspect='auto', extent=(0, 1, 0, 1), alpha=0.5)
        
        gs_menu = GridSpec(2, 3, figure=self.fig_menu, height_ratios=[5.5, 3], 
                    width_ratios=[1.5, 1.5, 1.5], 
                    left=0.1, right=0.9, top=0.95, bottom=0.1, 
                    wspace=0.05, hspace=0.5)
        
        ax_title = self.fig_menu.add_subplot(gs_menu[0, :])
        logo_img = Image.open("files//planisuss_logo.png")
        ax_title.imshow(logo_img)
        
        ax_title.set_title("Choose a map to start the simulation", loc='center', fontweight='bold')
        ax_title.axis('off')

        ax_map1 = self.fig_menu.add_subplot(gs_menu[1, 0])
        ax_map2 = self.fig_menu.add_subplot(gs_menu[1, 1])
        ax_map3 = self.fig_menu.add_subplot(gs_menu[1, 2])

        ax_map1.set_title("Map 1")
        ax_map1.imshow(Image.open(f"{self.MAP_PATHS}//map_seed_{self.WORLD_CONFIGS['map1']['seed']}.png"))
        ax_map1.axis('off')

        ax_map2.set_title("Map 2")
        ax_map2.axis('off')

        ax_map3.set_title("Map 3")
        ax_map3.axis('off')

        self.fig_menu.canvas.mpl_connect('button_press_event', lambda event: self.choose_map(self.fig_menu, event))
    
        self.fig_menu.show()
    
    def choose_map(self, fig_menu, event):
        if event.inaxes not in fig_menu.get_axes(): return

        _, title, map1, map2, map3 = list(fig_menu.get_axes())
        
        if event.inaxes == title:
                print('Title clicked')
        elif event.inaxes == map1:
            print("map1 clicked")
            self.selected_map = "map1"
            seed = self.WORLD_CONFIGS[self.selected_map]["seed"]
            self.set_environment(seed)
        elif event.inaxes == map2:
            print("map2 clicked")
            self.selected_map = "map2"
            seed = self.WORLD_CONFIGS[self.selected_map]["seed"]
            self.set_environment(seed)
        elif event.inaxes == map3:
            print("map3 clicked")
            self.selected_map = "map3"
            seed = self.WORLD_CONFIGS[self.selected_map]["seed"]
            self.set_environment(seed)

    def set_generation_type(self, type, nErb = 50, nCarv = 50):
        self.generation_type = type
        self.numErb = nErb
        self.numCarv = nCarv

    def set_environment(self, seed):
        environment = Environment(seed=seed)
        self.env = environment
        self.grid = self.gridToRGB(environment.getGrid(), save=True, seed=seed)
        # self.initialize_population(environment, type="random", nErb=100, nCarv=100)
        self.initialize_population(environment, self.generation_type, self.numErb, self.numCarv)
        self.create_map_and_start()

    def initialize_population(self, environment, type:str = "test1", nErb = 100, nCarv = 100):
        grid_shape = environment.getGrid().shape
        land_cells = [(x, y) for x in range(grid_shape[0]) for y in range(grid_shape[1])
                    if environment.isLand(x, y)]

        if type == "test1":
            erb1 = Erbast((25,25), energy=100, name="erb 1")
            erb2 = Erbast((25,25), energy=5, name="erb 2")
            erb3 = Erbast((25,25), energy=5, name="erb 3")
            herd1 = Herd([erb1,erb2,erb3])
            environment.add(herd1)

            erbOther = Erbast((24,25), energy=100, name="carv 4")
            erbOther2 = Erbast((24,25), energy=5, name = "carv 5")
            herd2 = Herd([erbOther, erbOther2])
            environment.add(herd2)

            carv1 = Carviz((24, 24))
            carv2 = Carviz((24, 24))
            pride1 = Pride([carv1,carv2])
            environment.add(pride1)

            carv3 = Carviz((26,26))
            carv4 = Carviz((26,26), SocialAttitude = 0.8)
            carv5 = Carviz((26,26))
            pride2 = Pride([carv3,carv4,carv5])
            environment.add(pride2)

        if type == "test2":
            erb1 = Erbast((25,25), energy=60, name="schiavo 1")
            carv1 = Carviz((24, 24))
            environment.add(erb1)
            environment.add(carv1)
            environment.add(Carviz((26,26)))

        if type == "test_offsprings":

            erbs = [
                Erbast((25,25)),
                Erbast((28,28)),
                Erbast((28,28)),
                Erbast((30,30))
            ]

            carvs = [
                Carviz((24, 24)),
                Carviz((27, 27)),
                Carviz((27, 27))
            ]

            for el in erbs:
                environment.add(el)
            for el in carvs:
                environment.add(el)

        if type == "one Erbast":
            erb = Erbast((25,25))
            environment.add(erb)

        if type == "random":
            for i in range(nErb):
                (x, y) = random.choice(land_cells)
                # coords = (random.randint(20,30), random.randint(20,30))
                erb = Erbast((x, y), SocialAttitude = random.random())
                environment.add(erb)

            for i in range(nCarv):
                (x, y) = random.choice(land_cells)
                # coords = (random.randint(20,30), random.randint(20,30))
                carv = Carviz((x, y), SocialAttitude = random.random())
                environment.add(carv)

    def create_map_and_start(self):
        plt.close(self.fig_menu)

        self._fig_map = self.create_fig_map()
        self._fig_map.canvas.mpl_connect('button_press_event', self.onclick)
        self.day_text = self.ax_plot.text(0.02, 0.95, f'Day 0', 
                                      bbox={'facecolor':'w', 'alpha':0.5}, 
                                      transform=self.ax_plot.transAxes)
        
        self.start()

    def create_fig_map(self):
        if self._fig_map is None:
            self._fig_map = plt.figure(figsize=(10, 10), dpi=100)
            self._fig_map.set_facecolor(self.COLORS)
            self.gs_map = GridSpec(2, 2, height_ratios=[5, 1], width_ratios=[5, 1], figure=self._fig_map)
            
            self.ax_plot = self._fig_map.add_subplot(self.gs_map[0, 0])
            self.ax_plot.set_aspect('equal', adjustable='box')
            self.ax_plot.axis('off')
            self.welcome_plot = self._fig_map.add_subplot(self.gs_map[0, 1])
            self.welcome_plot.text(0.5, 0.5, 
                                   f'Click on any cell\nto know more information', va='center', ha='center')
            self.welcome_plot.axis('off')
            self._fig_map.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.08, wspace=0.01, hspace=0.05)
            # self._fig_map.tight_layout(pad=1.0)
            self._fig_map.canvas.manager.set_window_title("Planisuss World")
            self.setup_controls()
        return self._fig_map


    def setup_controls(self):
        gs_controls = GridSpec(1, 3, figure=self._fig_map, height_ratios=[1], width_ratios=[1, 1, 1], left=0.1, right=0.9, top=0.15, bottom=0.07, wspace=0.05)
        controls = {
            'ax_pause' : (self._fig_map.add_subplot(gs_controls[0, 0]), "files//pause.png"),
            'ax_play' : (self._fig_map.add_subplot(gs_controls[0, 1]), "files//play.png"),
            'ax_x2' : (self._fig_map.add_subplot(gs_controls[0, 2]), "files//x2.png")
        
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
        self._fig_map.show()


    def update(self, frameNum, img):
        """Update the grid for animation."""
        
        self.currentDay = frameNum
        
        if self.currentDay >= self.maxDay:
            logger.info("Reached max days, stopping animation")
            self.ani.event_source.stop()
            return [img]
        
        logger.debug("Advancing simulation day")
        self.env.nextDay()

        img = self.ax_plot.imshow(self.grid, interpolation='nearest')
        print(f"{frameNum} and {self.currentDay}")
        self.day_text.set_text(f"Day: {self.currentDay}")
    
        for artist in self.vegetob_artists:
            artist.remove()
        self.vegetob_artists.clear()

        logger.debug("Drawing new elements")
        self.draw_elements(self.grid)

        logger.debug(f"Frame {frameNum} complete, returning {2 + len(self.alive_animal_artists) + len(self.vegetob_artists)} artists")
        
        return [img, self.day_text] + list(self.alive_animal_artists.values()) + list(self.dead_animal_artists.values()) + self.vegetob_artists
    
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
        dead_list = [dead.deadAnimal for dead in cell.getDeadCreaturesList()]
        
        # First, clear any alive animals that are now dead
        for dead in dead_list:
            if dead in self.alive_animal_artists:
                artist = self.alive_animal_artists[dead]
                artist.remove()
                del self.alive_animal_artists[dead]
    
        # Draw living animals
        for animal in erbast_list + carviz_list:
            if animal not in dead_list:
                logger.debug(f"Drawing living animal {animal} as Circle")
                self.draw_living_animal(animal)
        
        # Draw dead animals that haven't been processed yet
        for dead in dead_list:
            if dead not in self.dead_animal_artists and dead not in self.processed_dead_animals:
                logger.debug(f"Drawing dead animal {dead} as Rectangle")
                self.draw_dead_animal(dead)

    def draw_living_animal(self, animal):
        shift_x, shift_y = np.random.uniform(-0.3, 0.3, 2)
        x, y = animal.getCoords()
        
        if animal in self.alive_animal_artists:
            logger.debug(f"Updating position of existing living animal {animal}")
            # update position
            current_artist = self.alive_animal_artists[animal]
            current_artist.center = (y + shift_y, x + shift_x)
        else:
            logger.debug(f"Creating new artist for living animal {animal}")
            if isinstance(animal, Erbast):
                color = [216 / 255, 158 / 255, 146 / 255]
            else:
                color = [139 / 255, 0 / 255, 0 / 255]
            
            new_artist = Circle((y + shift_y, x + shift_x), radius=0.1, color=color, alpha=1)
            self.ax_plot.add_artist(new_artist)
            self.alive_animal_artists[animal] = new_artist
        
    def draw_dead_animal(self, animal):
        logger.debug(f"Drawing dead animal {animal} as Rectangle")
        shift_x, shift_y = np.random.uniform(-0.3, 0.3, 2)
        x, y = animal.getCoords()
        
        if isinstance(animal, Carviz):
            color = [253 / 255, 174 / 255, 69 / 255]
        else:
            color = [240 / 255, 255 / 255, 240 / 255]
        new_artist = Rectangle(xy=(y + shift_y, x + shift_x), 
                            width=0.2, height=0.2, 
                            color=color, fill=True, alpha=1)
        
        self.ax_plot.add_artist(new_artist)
        self.dead_animal_artists[animal] = new_artist
        self.processed_dead_animals.add(animal)

    def draw_vegetob(self, cell, i, j):
        cell_density = cell.getVegetobDensity()
        # print(f"cell density: {cell_density}")          
        green_intensity = int((cell_density / MAX_GROWTH) * 255) / 255
        color_vegetob = (0, green_intensity, 0)
        rectangle = plt.Rectangle((j - 0.5, i - 0.5), 1, 1, color=color_vegetob, alpha=0.4)
        self.ax_plot.add_artist(rectangle)
        self.vegetob_artists.append(rectangle)
    
    def _log_artist_map_state(self):
        """Log the current state of the animal_artists_map dictionary for debugging."""
        logger.debug(f"Current animal_artists_map contains {len(self.animal_artists_map)} entries")
        
        circle_count = 0
        rectangle_count = 0
        other_count = 0
        
        for animal, artist in self.animal_artists_map.items():
            if isinstance(artist, Circle):
                circle_count += 1
            elif isinstance(artist, Rectangle):
                rectangle_count += 1
            else:
                other_count += 1
        
        logger.debug(f"Artists by type: {circle_count} Circles, {rectangle_count} Rectangles, {other_count} other")
        
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

        
    def gridToRGB(self, grid, save=False, seed=None):
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
        
        if save and seed is not None:
            filepath = f"files//maps//map_seed_{seed}.png"
        
            if not os.path.exists(filepath):
                img = Image.fromarray(grid_rgb)
                img.save(filepath)
        
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
            self.ani = FuncAnimation(self._fig_map, self.update, frames=list(range(1, self.maxDay + 1)), fargs=(self.img,),
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

        for artist in self.alive_animal_artists.values():
            artist.remove()
        
        self.alive_animal_artists.clear()
        # self.animal_artists.clear()

        self.img = self.ax_plot.imshow(initial_grid, interpolation='nearest')
        self.draw_elements(initial_grid)
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
        cell_density = cell.getVegetobDensity()
        if cell_density < 25:
            img_cell = Image.open(self.IMAGE_PATHS['CELL']['DIRT'])
        elif 25 < cell_density < 50:
            img_cell = Image.open(self.IMAGE_PATHS['CELL']['GRASS_LOW'])
        elif 50 < cell_density < 100:
            img_cell = Image.open(self.IMAGE_PATHS['CELL']['GRASS_MED'])
        else:
            img_cell = Image.open(self.IMAGE_PATHS['CELL']['GRASS_HIGH'])
        
        fig = plt.figure(figsize=(5,5))
        gs = GridSpec(2, 2, height_ratios=[3, 1], figure=fig)
        ax_img = fig.add_subplot(gs[0, 0])
        
        # ax = ShowCard.remove_text(self.ax[1])
        extent = [0, 0.5, 0.5, 1]
        ax_img.imshow(img_cell, extent=extent)
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
        
        axis_erbast = self.axis_individuals(tot_erbast, fig, gs_animals, 0, erbast=True, carviz=False, list_animals= erbast_list, empty=erbast_empty, dead_empty=dead_empty)
        axis_carviz = self.axis_individuals(tot_carviz, fig, gs_animals, tot_erbast+1, erbast=False, carviz=True, list_animals = carviz_list, empty=carviz_empty, dead_empty=dead_empty)
        axis_dead = self.axis_individuals(tot_dead, fig, gs_animals, tot_erbast+tot_carviz+2, erbast=False, carviz=False, list_animals = dead_list, empty=dead_empty, dead_empty=dead_empty)   
        
        print("erbast axis", axis_erbast)
        print("carviz axis", axis_carviz)

        self.individuals_axis = axis_erbast + axis_carviz + axis_dead

        fig.canvas.draw()
        fig.show()

        fig.canvas.mpl_connect('button_press_event', lambda event: self.track_onclick(event, self.individuals_axis))
    
    def axis_individuals(self, n : int, fig, gs, start_row, erbast : bool, carviz : bool, list_animals : list, empty : bool, dead_empty : bool):
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

        if erbast and empty:
            s_empty = 'There are no Erbast in cell'
        elif carviz and empty:
            s_empty = 'There are no Carviz in cell'
        elif not erbast and not carviz and dead_empty:
            s_empty = 'There are no dead animals in cell'
        else:
            s_empty = 'No animals in this category'
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




