import numpy as np
import matplotlib as mpl
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
import itertools
import os
import json
import time

# Logging files for debugging the interface and the simulation
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

    It contains:
        - Constants for the visualization including colors and font sizes
        as well as some paths for the images used in the interface and the
        configurations of the maps
        - The init method that initializes the attributes of the class
            - The initialize_attributes method that initializes the attributes

    """
    # Dictionary with images paths
    IMAGE_PATHS = {
        'SOCIAL_ATT': {
            'ZERO' : 'files//SocialAtt0.png',
            'LOW': "files//SocAtt1.png",
            'MEDIUM': "files//SocAtt2.png",
            'HIGH': "files//SocAtt3.png"
        },
        'ENERGY': {
            'ZERO' : 'files//energy0.png',
            'LOW': "files//energy1.png",
            'MEDIUM': "files//energy2.png",
            'HIGH': "files//energy3.png"
        },
        'CELL': {
            'WATER': "files//water.png", 
            'DIRT' : "files//dirt.png",
            'GRASS_LOW' : "files//grass_low.png",
            'GRASS_MED' : "files//grass_med.png",
            'GRASS_HIGH' : "files//grass_high.png"
        }
    }

    # Constants for the visualization
    COLORS = (6/255, 32/255, 33/255, 0.8)
    FONT_COLOR = (234/255, 222/255, 204/255)
    AXES_COLOR = (147/255, 91/255, 78/255, 0.3)
    CARVIZ_COLOR = (192/255, 17/255, 0)
    ERBAST_COLOR = (216/255, 158/255, 146/255)
    CARVIZ_TOMB = (255 / 255, 156/255, 36/255)
    ERBAST_TOMB = (240/255, 255/255, 240/255)
    HERD_COLOR = [201/255, 212/255, 135/255]
    PRIDE_COLOR = [203/255, 77/255, 38/255]

    # Setting the matplotlib parameters
    mpl.rcParams['figure.facecolor'] = COLORS
    mpl.rcParams['axes.facecolor'] = AXES_COLOR
    mpl.rcParams['text.color'] = FONT_COLOR
    mpl.rcParams['axes.edgecolor'] = AXES_COLOR
    mpl.rcParams['font.family'] = 'Comic Sans MS'
    mpl.rcParams['font.size'] = 11
    mpl.rcParams['font.weight'] = 'bold'
    mpl.rcParams['axes.titlesize'] = 16
    mpl.rcParams['xtick.color'] = FONT_COLOR
    mpl.rcParams['xtick.major.size'] = 1.0
    mpl.rcParams['ytick.major.size'] = 1.0
    mpl.rcParams['ytick.color'] = FONT_COLOR
    mpl.rcParams['ytick.labelcolor'] = FONT_COLOR
    mpl.rcParams['lines.linewidth'] = 1.5

    # Constants for the maps
    WORLD_CONFIGS = {}
    CHOOSEN_MAPS = {}
    MAP_PATHS = "files//maps"
    MAPS_FILE = "files//maps_file.json"

    def __init__(self):
        # method for initializing the attributes
        self.initialize_attributes()
        self._fig_map = None
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
        self.tomb_show = True
        self.old_tombs = set()
        self.button_pressed_play = False
        self.button_pressed_pause = False
        self.stats_pressed = False
        self.interval_val = 2000

    def env_params(self, dynamic):
        """
        Generate a set of random parameters for the world generation
        The world is generated using Brownian motion with a set of parameters
        Parameters:
            - seeds : random seeds for the generation
            - thresholds : thresholds for the balance between land and water
            - octaves : for generating more detailed coasts
            - persistences : for more pronounced terrain features
            - lacunarities : for more clustered island groups
            - scales : for more islands
            - dynamic : if true the generation will start from the center of the map
            avoiding creation of land masses in the borders
        """
        # getting the parameters
        n_samples = 50
        seeds = np.random.randint(1, 100, size=n_samples)
        thresholds = np.random.uniform(0.4, 0.6, size=n_samples)
        octaves_p = np.random.randint(30, 50, size=n_samples)
        persistences = np.random.uniform(0.3, 0.4, size=n_samples)
        lacunarities = np.random.uniform(1.9, 2.5, size=n_samples)
        scales = np.random.randint(15, 25, size=n_samples)

        # inserting the parameters in the dictionary
        for i, seed in enumerate(seeds):
            threshold = thresholds[i]
            octaves = octaves_p[i]
            persistence = persistences[i]
            lacunarity = lacunarities[i]
            scale = scales[i]

            self.WORLD_CONFIGS[f"map{i+1}"] = {
                "path" : f"{self.MAP_PATHS}//map_random_seed_{seed}.png",
                "seed": seed,
                "threshold": threshold,
                "octaves": octaves,
                "persistence": persistence,
                "lacunarity": lacunarity,
                "scale": scale,
                "dynamic": dynamic
            }

        # saving the parameters to a file
        self.save_to_file()
        
        return self.WORLD_CONFIGS

    def save_to_file(self):
        """Save map configurations to JSON file"""
        # encoding the numpy datatypes into datatypes that can be read by json
        serializable_configs = {}
        
        for map_name, config in self.WORLD_CONFIGS.items():
            serializable_configs[map_name] = {
                "path" : config["path"],
                "seed": int(config["seed"]),
                "threshold": float(config["threshold"]),
                "octaves": int(config["octaves"]),
                "persistence": float(config["persistence"]),
                "lacunarity": float(config["lacunarity"]),
                "scale": int(config["scale"]),
                "dynamic": config["dynamic"]
            }

        # this is the case we want to add new configurations to the existing ones
        existing_configs = {}
        if os.path.exists(self.MAPS_FILE):
            with open(self.MAPS_FILE, 'r') as f:
                try:
                    existing_configs = json.load(f)
                    print(existing_configs)
                except json.JSONDecodeError:
                    print("error")
                    existing_configs = {}

        existing_configs.update(serializable_configs)
        
        with open(self.MAPS_FILE, 'w') as f:
            json.dump(existing_configs, f, indent=4)
        
        print(f"Added {len(serializable_configs)} new map configurations to {self.MAPS_FILE}")
        print(f"Total configurations: {len(existing_configs)}")

    def load_configs(self):
        """
        Load map configurations from JSON file
        """
        if os.path.exists(self.MAPS_FILE):
            with open(self.MAPS_FILE, 'r') as f:
                self.CHOOSEN_MAPS = json.load(f)
            print(f"Loaded {len(self.CHOOSEN_MAPS)} map configurations from {self.MAPS_FILE}")
        else:
            print(f"No map configurations found in {self.MAPS_FILE}") # empty configurations handling

    def run_simulation(self, map_selection=False, dynamic=False):
        """
        Main method for running the simulation, if map_selection is True then it will not
        show the menu and the simulation will not start it only serves for map generation.
        If map_selection is False then the simulation will start and the maps can be selected
        from the start menu
        """
        if map_selection:
            env_params = self.env_params(dynamic)
            for map_name, config in env_params.items():
                self.set_params_env(map_name)
        else:
            plt.ion() 
            self.start_menu()
            plt.show(block=True)

    def start_menu(self):
        """
        Start menu for the simulation, it will show the available maps and the logo of the project
        """
        self.load_configs() # getting the json configurations

        # creating the matplolib figure for the menu
        self.fig_menu = plt.figure(figsize=(8,8), dpi=100)
        self.fig_menu.set_facecolor(self.COLORS)
        
        background_ax = self.fig_menu.add_axes([0, 0, 1, 1])
        background_img = Image.open("files//background.jpg")
        background_ax.imshow(background_img, aspect='auto', extent=(0, 1, 0, 1), alpha=0.5)
        
        # creating the grid in the figure for the menu that will contain the axis for each map 
        gs_menu = GridSpec(3, 3, figure=self.fig_menu, height_ratios=[5.5, 3, 3], 
                    width_ratios=[1.5, 1.5, 1.5], 
                    left=0.1, right=0.9, top=0.95, bottom=0.1, 
                    wspace=0.05, hspace=0.5)
        
        ax_title = self.fig_menu.add_subplot(gs_menu[0, :])
        logo_img = Image.open("files//planisuss_logo.png")
        ax_title.imshow(logo_img)
        
        ax_title.set_title("Choose a map to start the simulation", loc='center', fontweight='bold',
                           color=[253/255, 253/255, 198/255])
        ax_title.axis('off')

        ax_map1 = self.fig_menu.add_subplot(gs_menu[1, 0])
        ax_map2 = self.fig_menu.add_subplot(gs_menu[1, 1])
        ax_map3 = self.fig_menu.add_subplot(gs_menu[1, 2])
        ax_map4 = self.fig_menu.add_subplot(gs_menu[2, 0])
        ax_map5 = self.fig_menu.add_subplot(gs_menu[2, 1])
        ax_map6 = self.fig_menu.add_subplot(gs_menu[2, 2])

        map_names = list(self.CHOOSEN_MAPS.keys())
    
        ax_map1.set_title("Map 1")
        ax_map1.imshow(Image.open(self.CHOOSEN_MAPS[map_names[0]]["path"]))
        ax_map1.axis('off')

        ax_map2.set_title("Map 2")  
        ax_map2.imshow(Image.open(self.CHOOSEN_MAPS[map_names[1]]["path"]))
        ax_map2.axis('off')

        ax_map3.set_title("Map 3")
        ax_map3.imshow(Image.open(self.CHOOSEN_MAPS[map_names[2]]["path"]))
        ax_map3.axis('off')

        ax_map4.set_title("Map 4")
        ax_map4.imshow(Image.open(self.CHOOSEN_MAPS[map_names[3]]["path"]))
        ax_map4.axis('off')

        ax_map5.set_title("Map 5")
        ax_map5.imshow(Image.open(self.CHOOSEN_MAPS[map_names[4]]["path"]))
        ax_map5.axis('off')

        ax_map6.set_title("Map 6")
        ax_map6.imshow(Image.open(self.CHOOSEN_MAPS[map_names[5]]["path"]))
        ax_map6.axis('off')

        # connecing the figure with the button press event to trigger a function when an axis is clicked
        self.fig_menu.canvas.mpl_connect('button_press_event', lambda event: self.choose_map(self.fig_menu, event))
    
        self.fig_menu.show()
    
    def choose_map(self, fig_menu, event):
        """
        The triggered fuction to choose the maps from the menu
        """
        if event.inaxes not in fig_menu.get_axes(): return # if the click is not in the axes return 

        _, title, map1, map2, map3, map4, map5, map6 = list(fig_menu.get_axes())
        
        if event.inaxes == title:
            print('Title clicked')
        elif event.inaxes == map1:
            print("map1 clicked")
            map_name = list(self.CHOOSEN_MAPS.keys())[0]
            self.selected_map = map_name
            self.set_params_env(map_name)
        elif event.inaxes == map2:
            print("map2 clicked")
            map_name = list(self.CHOOSEN_MAPS.keys())[1]
            self.selected_map = map_name
            self.set_params_env(map_name)
        elif event.inaxes == map3:
            print("map3 clicked")
            map_name = list(self.CHOOSEN_MAPS.keys())[2]
            self.selected_map = map_name
            self.set_params_env(map_name)
        elif event.inaxes == map4:
            print("map4 clicked")
            map_name = list(self.CHOOSEN_MAPS.keys())[3]
            self.selected_map = map_name
            self.set_params_env(map_name)
        elif event.inaxes == map5:
            print("map5 clicked")
            map_name = list(self.CHOOSEN_MAPS.keys())[4]
            self.selected_map = map_name
            self.set_params_env(map_name)
        elif event.inaxes == map6:
            print("map6 clicked")
            map_name = list(self.CHOOSEN_MAPS.keys())[5]
            self.selected_map = map_name
            self.set_params_env(map_name)

    def set_params_env(self, map_name, select_map=False):
        """
        Function for setting up the parameters of the choosen map into the environment 
        """
        if map_name in self.CHOOSEN_MAPS:
            config = self.CHOOSEN_MAPS[map_name]
            seed = config["seed"]
            threshold = config["threshold"]
            octaves = config["octaves"]
            persistence = config["persistence"]
            lacunarity = config["lacunarity"]
            scale = config["scale"]
            dynamic = config["dynamic"]
        else:
            config = self.WORLD_CONFIGS[map_name]
            seed = config["seed"]
            threshold = config["threshold"]
            octaves = config["octaves"]
            persistence = config["persistence"]
            lacunarity = config["lacunarity"]
            scale = config["scale"]
            dynamic = config["dynamic"]

        # only the 6th map uses dynamic generation
        if seed == 1:
            print("Seed 1 setting dynamic=True")
            dynamic = True
        
        self.set_environment(threshold, seed, octaves, persistence, lacunarity, scale, dynamic, select_map)

    def set_environment(self, thr, seed, octv, per, lacu, scl, dynamic, select_map=False):
        """
        Setting up the environment and coloring it.
        Important argument: select_map, if True the simulation will not start and only the map will be 
        colored and generated
        """
        environment = Environment(threshold=thr, seed=seed, octaves=octv, persistence=per, lacunarity=lacu, scale=scl, dynamic=dynamic)
        self.env = environment
        self.grid = self.gridToRGB(environment.getGrid(), save=True, seed=seed)
        if not select_map: 
            self.initialize_population(environment, self.generation_type, self.numErb, self.numCarv)
            self.create_map_and_start()
        else:
            return
        
    def set_generation_type(self, type, nErb = 50, nCarv = 50):
        """
        Helper function for setting up how the population will be generated
        """
        self.generation_type = type
        self.numErb = nErb
        self.numCarv = nCarv

    def initialize_population(self, environment, type:str = "test1", nErb = 100, nCarv = 100):
        """
        Method for initializing the population, it filters out the water cells and has only some
        of the initial tests we did for testing some features of the simulation.
        Recommened to use the random type for generating the population
        """
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
                erb = Erbast((x, y), SocialAttitude = random.random())
                environment.add(erb)

            for i in range(nCarv):
                (x, y) = random.choice(land_cells)
                carv = Carviz((x, y), SocialAttitude = random.random())
                environment.add(carv)

    def create_map_and_start(self):
        """
        Creating figure for the map and starting the simulation after closing
        the menu
        """
        plt.close(self.fig_menu)
        self._fig_map = self.create_fig_map()
        self._fig_map.canvas.mpl_connect('button_press_event', self.onclick)
        self.day_text = self.ax_plot.text(0.02, 0.95, f'Day 0', 
                                      bbox={'facecolor':'w', 'alpha':0.5}, 
                                      transform=self.ax_plot.transAxes)
        
        self.start()

    def create_fig_map(self):
        """
        Creating the figure for the map and setting up the axis for the buttons
        in order to interacr with them
        """
        if self._fig_map is None:
            self._fig_map = plt.figure(figsize=(10, 10), dpi=100)
            self._fig_map.set_facecolor(self.COLORS)
            self.gs_map = GridSpec(2, 2, height_ratios=[5, 1], width_ratios=[6, 1.5], figure=self._fig_map)
            
            self.ax_plot = self._fig_map.add_subplot(self.gs_map[0, 0])
            self.ax_plot.axis('off')
            self.welcome_plot = self._fig_map.add_subplot(self.gs_map[0, 1])
            self.welcome_plot.set_title("Click on any cell\nto know more information", loc='center', fontsize=11, weight='bold')
            self.welcome_plot.imshow(Image.open("files//labels_animals.png"))
            self.welcome_plot.axis('off')
            self._fig_map.subplots_adjust(left=0.02, right=0.8, top=0.98, bottom=0.08, wspace=0.5, hspace=0.05)
            self._fig_map.canvas.manager.set_window_title("Planisuss World")
            self.setup_controls()
        return self._fig_map

    def setup_controls(self):
        """
        Setting up the grid with the axis of the controls that were defined in a dictionary
        with their corresponding path to the images to facilitate their creation
        """
        gs_controls = GridSpec(1, 5, figure=self._fig_map, height_ratios=[1], width_ratios=[2, 2, 2, 2, 2], left=0.1, right=0.9, top=0.15, bottom=0.07, wspace=0.05)
        controls = {
            'ax_pause' : (self._fig_map.add_subplot(gs_controls[0, 0]), "files//pause.png"),
            'ax_play' : (self._fig_map.add_subplot(gs_controls[0, 1]), "files//test.png"),
            'ax_x2' : (self._fig_map.add_subplot(gs_controls[0, 2]), "files//x2.png"),
            'ax_tombs' : (self._fig_map.add_subplot(gs_controls[0, 3]), "files//tombs.png"),
            'ax_stats' : (self._fig_map.add_subplot(gs_controls[0, 4]), "files//stats.png")
        }
        for name, (ax, pathImg) in controls.items():   
            try:
                img = Image.open(pathImg)
                ax.imshow(img)
                ax.axis('off')
                setattr(self, name, ax)
            except FileNotFoundError:
                print('The image was not found')
                img = None
                setattr(self, name, None)
        self._fig_map.show()


    def update(self, frameNum, img):
        """
        Most important function for the animation, it updates the frame and the image
        This function will be called each frame (new day) so that all animals can be
        updated / redrawn on the image
        """ 
        
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
        self.draw_elements(self.grid, self.currentDay)

        # updating the interval of the animation for faster animation
        if self.faster:
            self.ani.event_source.interval = self.interval_val
        else:
            self.ani.event_source.interval = 2000
        # print(self.ani.event_source.interval)

        logger.debug(f"Frame {frameNum} complete, returning {2 + len(self.alive_animal_artists) + len(self.vegetob_artists)} artists")
        
        return [img, self.day_text] + list(self.alive_animal_artists.values()) + list(self.dead_animal_artists.values()) + self.vegetob_artists
    
    def draw_elements(self, grid, day):
        """
        This function scans cell by cell of the grid and draws the animals and the vegetob
        """
        for i in range(grid.shape[0]):
            for j in range(grid.shape[1]):
                cell = self.env.getGrid()[i, j]
                if isinstance(cell, LandCell):
                    self.draw_animals_in_cell(cell, day)
                    self.draw_vegetob(cell, i, j)

    def draw_animals_in_cell(self, cell, day):
        """
        Draw all animals in a cell for a specific day
        It will access the amount of animals in a cell using the getErbastList and getCarvizList
        and draw them as circles with the corresponding color with the draw_living_animal. In the case of dead creatures
        the function draw_dead_animal will be called to draw them as rectangles
        """
        erbast_list = cell.getErbastList()
        carviz_list = cell.getCarvizList()
        dead_list = [dead.deadAnimal for dead in cell.getDeadCreaturesList()]
        
        # First we want to remove the artists of any animal that was alive 
        # but is now dead
        for dead in dead_list:
            if dead in self.alive_animal_artists:
                artist = self.alive_animal_artists[dead]
                artist.remove()  # remove the artist from the plot
                del self.alive_animal_artists[dead] # and also from the dictionary
    
        # Draw living animals
        for animal in erbast_list + carviz_list:
            if animal not in dead_list:
                logger.debug(f"Drawing living animal {animal} as Circle")
                self.draw_living_animal(animal)
        
        # Draw dead animals that were not drawn before
        for dead in dead_list:
            if dead not in self.dead_animal_artists and dead not in self.processed_dead_animals:
                logger.debug(f"Drawing dead animal {dead} as Rectangle")
                self.draw_dead_animal(dead, day)
            else:
                self.draw_dead_animal(dead, day, remove=True)

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
                color = self.ERBAST_COLOR
            else:
                color = self.CARVIZ_COLOR
            
            new_artist = Circle((y + shift_y, x + shift_x), radius=0.1, color=color, alpha=1)
            self.ax_plot.add_artist(new_artist)
            self.alive_animal_artists[animal] = new_artist
        
    def draw_dead_animal(self, animal, day, remove=False):
        """
        Draws dead animals as rectangles also is responsible for not showing the tombs
        of the animals after three days of their death to prevent cluttering of the map
        Note: This feature is regulated by whether the user wants to see the tombs or not
        if the user wants to see the tombs even after 3 days they will still be visible   
        """
        logger.debug(f"Drawing dead animal {animal} as Rectangle")
        shift_x, shift_y = np.random.uniform(-0.3, 0.3, 2)
        x, y = animal.getCoords()
        
        if remove is False:
            if isinstance(animal, Carviz):
                color = self.CARVIZ_TOMB
            else:
                color = self.ERBAST_TOMB
            new_artist = Rectangle(xy=(y + shift_y, x + shift_x), 
                                width=0.2, height=0.2, 
                                color=color, fill=True, alpha=1)
            
            self.ax_plot.add_artist(new_artist)
            self.dead_animal_artists[animal] = new_artist
            self.processed_dead_animals.add((animal, day))
        else:
            dead_day = 0
            for dead, d in self.processed_dead_animals:
                if dead == animal:
                    dead_day = d
                    break
            if day - dead_day >= 3:
                # print("Removing dead animal after 3 days")
                if animal not in self.old_tombs:
                    self.old_tombs.add(animal)
                if not self.tomb_show:
                    self.dead_animal_artists[animal].set_visible(False)
            else:
                # print("Not enough days have passed")
                self.dead_animal_artists[animal].set_visible(self.tomb_show)

    def remove_tombs(self):
        """
        This is a helper function for removing all the tombs from the map if the user
        desires to do so
        """
        # print("Removing all tombs")
        for dead, artist in self.dead_animal_artists.items():
            artist.set_visible(False)
    
    def display_tombs(self):
        """
        This is a helper function for displaying all the tombs on the map if the user
        desires to do so
        """
        for dead, artist in self.dead_animal_artists.items():
            artist.set_visible(True)

    def draw_vegetob(self, cell, i, j):
        """
        This function will draw the density of the vegetob on the map
        The color is set based on the density of vegetobs in the cell
        More intesive green color => more vegetobs
        Less intnsive green color / brownish tones => less vegetobs
        """
        cell_density = cell.getVegetobDensity()         
        green_intensity = int((cell_density / MAX_GROWTH) * 255) / 255
        color_vegetob = (0, green_intensity, 0)
        rectangle = plt.Rectangle((j - 0.5, i - 0.5), 1, 1, color=color_vegetob, alpha=0.4)
        self.ax_plot.add_artist(rectangle)
        self.vegetob_artists.append(rectangle)
    
    def _log_artist_map_state(self):
        """
        Log the current state of the animal_artists_map dictionary for debugging
        """
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
        """
        Function for handling the click events on the main figure map
        It will track which axis or cells were clicked by the user and trigger the corresponding
        functions. 
            - The bottons will change color when clicked, the bottons:
                - Play / Pause will start or pause the animation
                - x5 will increase the speed of the animation
                - Tombs will toggle the visibility of the tombs
                - Stats will show the statistics of the simulation up to the current day 
            - If the user clicks on a cell the animation will be paused and information about
            the cell will be shown
        """
        if event.inaxes not in [self.ax_pause, self.ax_play, self.ax_x2, self.ax_tombs, self.ax_stats, self.ax_plot]: return
        
        x, y = event.xdata, event.ydata
        # print(self.grid.shape)
        grid_height, grid_width = self.grid.shape[0], self.grid.shape[1]
        cell_width = (self.ax_plot.get_xlim()[1] - self.ax_plot.get_xlim()[0]) / grid_width
        cell_height = (self.ax_plot.get_ylim()[0] - self.ax_plot.get_ylim()[1]) / grid_height
        grid_x = int((y - self.ax_plot.get_ylim()[1]) // cell_height)
        grid_y = int((x - self.ax_plot.get_xlim()[0]) // cell_width)
        
        if event.inaxes == self.ax_play:
            print('Play clicked')
            self.button_pressed_play = True
            if self.button_pressed_play:
                self.ax_play.imshow(Image.open("files//test2.png"))
            if self.button_pressed_pause:
                self.ax_pause.imshow(Image.open("files//pause.png"))
                self.button_pressed_pause = False
            if not self.anim_running:
                self.start()
            else:
                self.button_pressed_play = False
                self.ax_play.imshow(Image.open("files//test.png"))
                self.pause_animation()
        elif event.inaxes == self.ax_x2:
            print("x5 clicked")
            self.ax_x2.imshow(Image.open("files//x5_clicked.png"))
            if self.faster:
                print("Reverting to normal speed")
                self.ax_x2.imshow(Image.open("files//x2.png"))
                self.normal_animation()
            else:
                self.faster_animation()
        elif event.inaxes == self.ax_plot:
            if self.anim_running:
                self.pause_animation() # pausing the animation after clicking on the map
            print(f"cell {grid_x,grid_y} has been clicked")
            self.show_cell_info(grid_x, grid_y)
        elif event.inaxes == self.ax_tombs:
            print('Tombs clicked, removing all tombs')
            self.tomb_show = not self.tomb_show
            if not self.tomb_show:
                self.ax_tombs.imshow(Image.open("files//tombs_clicked.png"))
                self.remove_tombs()
            else:
                print('Tombs clicked again, displaying all tombs')
                self.ax_tombs.imshow(Image.open("files//tombs.png"))
                self.display_tombs()
        elif event.inaxes == self.ax_stats:
            print('Stats clicked')
            self.pause_animation()
            self.stats_pressed = True
            if self.stats_pressed:
                self.ax_stats.imshow(Image.open("files//stats_clicked.png"))
            else:
                self.ax_stats.imshow(Image.open("files//stats.png"))
            if self.currentDay < 4:
                    show_f = False
                    self.show_stats(show_f)
                    self.stats_pressed = False
                    self.ax_stats.imshow(Image.open("files//stats.png"))
                    self.start()
            else:
                show_f = True    
                self.show_stats(show_f)
        else:
            print('Stop clicked')
            if not self.button_pressed_pause:
                self.button_pressed_pause = True
                self.ax_pause.imshow(Image.open("files//pause_clicked.png"))
            else:
                self.ax_pause.imshow(Image.open("files//pause.png"))
                self.button_pressed_pause = False
            if self.button_pressed_play:
                self.ax_play.imshow(Image.open("files//test.png"))
                self.button_pressed_play = False
            self.pause_animation()
            
    def show_stats(self, show_f=True):
        """
        Function to plot some statistics of the simulation up to the current day
            - If the botton is clicked before the 4th day no stats will be shown and the window will
            automatically close after 3 seconds
            - If the botton is clicked after the 4th day the stats will be shown and the window will
            stay open until the user closes it, after closing it the simulation will automatically resume
        """
        stats = self.env.statistics
        was_running = self.anim_running

        def ticks_format(days, ax):
            """
            Helper function for formatting the ticks of the x-axis of the plots
            So that the days are correctly displayed
            """
            if len(days) >= 10:
                if len(days) >= 200:
                    ticks = [d for d in days if d % 100 == 0]
                elif len(days) >= 100:
                    ticks = [d for d in days if d % 50 == 0]
                elif len(days) >= 50:
                    ticks = [d for d in days if d % 20 == 0]
                elif len(days) >= 20:
                    ticks = [d for d in days if d % 10 == 0]
                else: 
                    ticks = [d for d in days if d % 5 == 0]
                
                # We want day 0 and current day to be shown
                if days[0] not in ticks:
                    ticks.insert(0, days[0])
                if days[-1] not in ticks:
                    ticks.append(days[-1])

                ax.set_xticks(ticks)
            else:
                ax.set_xticks(days)

        fig_stats = plt.figure(figsize=(15, 12), dpi=100)
        if not show_f:
            fig_stats.suptitle("Not enough days to show stats", fontsize=16)
            timer = fig_stats.canvas.new_timer(interval=3000)
            timer.add_callback(lambda: plt.close(fig_stats))
            timer.start()
            fig_stats.show()

            return
        
        days = [0] + list(range(1, self.currentDay+1))
        
        if len(days) < 4:
            print("Not enough days to show stats")

        # Axis for the population dynamics (Number of Erbasts and Carvizes)
        ax1 = fig_stats.add_subplot(3, 3, 1)
        ax1.plot(days, stats["Number of Erbasts"], label="Erbast", color=self.ERBAST_COLOR)
        ax1.plot(days, stats["Number of Carvizes"], label="Carviz", color=self.CARVIZ_COLOR)
        ax1.set_title("Population dynamics", fontsize=10, color=self.FONT_COLOR)
        ax1.set_xlabel("Days", fontsize=8, color=self.FONT_COLOR)
        ticks_format(days, ax1)
        ax1.set_ylabel("Population", fontsize=8, color=self.FONT_COLOR)
        ax1.legend(fontsize=6)
        ax1.grid(True, alpha=0.3)

        # Axis for the population growth rates and their growth difference each day
        ax2 = fig_stats.add_subplot(3, 3, 2)
        ax2.grid(True, alpha=0.3)
        erb_change = [stats["Number of Erbasts"][i+1] - stats["Number of Erbasts"][i] 
                 for i in range(len(days)-1)]
        carv_change = [stats["Number of Carvizes"][i+1] - stats["Number of Carvizes"][i] 
                  for i in range(len(days)-1)]
        # computing the difference between the growth rates of Erbasts and Carvizes
        growth_diff = [erb - carv for erb, carv in zip(erb_change, carv_change)]
        ax2.plot(days[1:], erb_change, label="Erbast", color=self.ERBAST_COLOR)
        ax2.plot(days[1:], carv_change, label="Carviz", color=self.CARVIZ_COLOR)

        # Creating a second y-axis for the growth difference
        ax2b = ax2.twinx()
        ax2b.bar(days[1:], growth_diff, color=[173/255, 142/255, 139/255], alpha=0.5, label="Growth difference")
        ax2b.axhline(0, color=self.FONT_COLOR, linestyle='--', alpha=0.5)
        ax2.set_title("Population Growth Rates", fontsize=10, color=self.FONT_COLOR)
        ax2.set_xlabel("Days", fontsize=8, color=self.FONT_COLOR)
        ticks_format(days, ax2)
        # ax2.set_xticks(days)
        ax2.set_ylabel("Daily Population Change", fontsize=8, color=self.FONT_COLOR)
        ax2b.set_ylabel("Growth Difference (Erb-Carv)", fontsize=8, color=self.FONT_COLOR)
        ax2.legend(loc='upper left', fontsize=6)
        ax2b.legend(loc='upper right', fontsize=6)

        # Plotting number of herds and prides and the average social attitudes
        ax3 = fig_stats.add_subplot(3, 3, 3)
        ax3.grid(True, alpha=0.3)
        ticks_format(days, ax3)
        ax3.set_xlabel("Days", fontsize=8, color=self.FONT_COLOR)
        ax3.plot(days, stats["Number of Herds"], label="Herd", color=self.HERD_COLOR)
        ax3.plot(days, stats["Number of Prides"], label="Pride", color=self.PRIDE_COLOR)
        ax3.set_ylabel("Number of Groups", fontsize=8, color=self.FONT_COLOR)
        ax3.legend(loc='upper left', fontsize=6)
        ax3.set_title("Group Dynamics", fontsize=10, color=self.FONT_COLOR)
        
        # Another y-axis for the average social attitudes
        ax3b = ax3.twinx()
        ax3b.plot(days, stats["Average Erbast Social Attitude"], label="Avg Erbast Social Attitude", color=self.HERD_COLOR, linestyle='--')
        ax3b.plot(days, stats["Average Carviz Social Attitude"], label="Avg Carviz Social Attitude", color=self.PRIDE_COLOR, linestyle='--')
        ax3b.set_ylabel("Average Social Attitude", color=self.FONT_COLOR, fontsize=8)
        ax3b.legend(loc='upper right', fontsize=6)

        # Plotting average herd and pride sizes
        ax4 = fig_stats.add_subplot(3, 3, 4)
        ax4.grid(True, alpha=0.3)
        ticks_format(days, ax4)
        ax4.set_xlabel("Days", fontsize=8, color=self.FONT_COLOR)
        ax4.set_ylabel("Average Group Size", fontsize=8, color=self.FONT_COLOR)
        ax4.set_title("Average Group Sizes", fontsize=10, color=self.FONT_COLOR)
        ax4.plot(days, stats["Average Herd Size"], color=[204/255, 212/255, 158/255], label="Avg Herd Group Size")
        ax4.plot(days, stats["Average Pride Size"], color=[203/255, 169/255, 159/255], label="Avg Pride Group Size")
        ax4.legend(fontsize=6)

        # Plotting energy levels and vegetob density (Resources and Energy)
        ax5 = fig_stats.add_subplot(3, 3, 5)
        ax5.grid(True, alpha=0.3)
        ticks_format(days, ax5)
        # ax5.set_xticks(days)
        ax5.set_xlabel("Days", fontsize=8, color=self.FONT_COLOR)
        ax5.set_ylabel("Energy Levels", fontsize=8, color=self.FONT_COLOR)
        ax5.set_title("Energy Levels and Resources", fontsize=10, color=self.FONT_COLOR)
        ax5.plot(days, stats["Average Erbast Energy"], label="Avg Erbast Energy", color=self.ERBAST_COLOR)
        ax5.plot(days, stats["Average Carviz Energy"], label="Avg Carviz Energy", color=self.CARVIZ_COLOR)
        ax5.legend(fontsize=6)
        
        # Vegetob density
        ax5b = ax5.twinx()
        ax5b.plot(days, stats["Average Vegetob Density"], label="Avg Vegetob Density", color=[0, 0.5, 0], linestyle='--')
        ax5b.set_ylabel("Average Vegetob Density", fontsize=8, color=self.FONT_COLOR)
        ax5b.legend(loc='lower left', fontsize=6)

        # Plotting Pred - Prey ratio
        ax6 = fig_stats.add_subplot(3, 3, 6)
        ax6.grid(True, alpha=0.3)
        ticks_format(days, ax6)
        ax6.set_xlabel("Days", fontsize=8, color=self.FONT_COLOR)
        ax6.set_ylabel("Predator-Prey Ratio", fontsize=8, color=self.FONT_COLOR)
        ax6.set_title("Predator-Prey Ratio", fontsize=10, color=self.FONT_COLOR)
        pred_prey_ratio = [car / erb if erb > 0 else 0 
                           for erb, car in zip(stats["Number of Erbasts"], stats["Number of Carvizes"])]
        ax6.plot(days, pred_prey_ratio, label="Predator-Prey Ratio", color=[247/255, 179/255, 204/255])
        ax6.legend(fontsize=6)

        # Hunting Metrics: Number of Hunts and Number of Successful Hunts
        ax7 = fig_stats.add_subplot(3, 3, 7)
        ax7.grid(True, alpha=0.3)
        ticks_format(days, ax7)
        ax7.set_xlabel("Days", fontsize=8, color=self.FONT_COLOR)
        ax7.set_ylabel("Number of Hunts", fontsize=8, color=self.FONT_COLOR)
        ax7.set_title("Number of Hunts & Successfulf Hunts", fontsize=10, color=self.FONT_COLOR)
        ax7.plot(days, stats["Number of Hunts"], label="N of Hunts", color=[235/255, 220/255, 251/255])
        ax7.plot(days, stats["Successfull Hunts"], label="N of Successfull Hunts", color=[232/255, 129/255, 112/255])
        ax7.legend(loc='lower left', fontsize=6)

        # Plotting success rate of hunts
        ax7b = ax7.twinx()
        success_rate = [succ_h / num_h if num_h > 0 else 0 
                        for succ_h, num_h in zip(stats["Successfull Hunts"], stats["Number of Hunts"])]
        ax7b.plot(days, success_rate, label="Success Rate", color=[132/255, 185/255, 191/255], linestyle='--')
        ax7b.set_ylabel("Success Rate", fontsize=8, color=self.FONT_COLOR)
        ax7b.legend(loc='lower right',fontsize=6)
    
        # Plotting the number of Deaths
        ax8 = fig_stats.add_subplot(3, 3, 8)
        ax8.grid(True, alpha=0.3)
        ticks_format(days, ax8)
        # ax8.set_xticks(days)
        ax8.set_xlabel("Days", fontsize=8, color=self.FONT_COLOR)
        ax8.set_ylabel("Deaths", fontsize=8, color=self.FONT_COLOR)
        ax8.set_title("Deaths", fontsize=10, color=self.FONT_COLOR)
        ax8.plot(days, stats["Number of Dead Creatures"], label="Deaths", color=[243/255, 230/255, 185/255])
        ax8.legend(fontsize=6)

        def on_close(event):
            """
            Function to track the closing of the stats window so that the simulation can resume
            """
            if not was_running:
                self.stats_pressed = False
                self.ax_stats.imshow(Image.open("files//stats.png"))
                self.start()

        # connecting the figure to the close event
        fig_stats.canvas.mpl_connect('close_event', on_close)
        fig_stats.subplots_adjust(
            left=0.1,            
            right=0.9,           
            top=0.95,           
            bottom=0.05,         
            wspace=0.5,          
            hspace=0.4 
            )          
        # fig_stats.tight_layout()
        fig_stats.show()

    def gridToRGB(self, grid, save=False, seed=None):
        """
        This method translates the environment grid to an RGB matrix for visualizationù
        It will color the land cells with a brownish color and the water cells with a blue color
        At the same time a gradient will be applied to smooth the colors of the map
        """
        grid_rgb = np.zeros((grid.shape[0], grid.shape[1], 3), dtype=np.uint8)
        get_type = np.vectorize(lambda cell: cell.getCellType()) # Tipo di cella
        cell_types = get_type(grid) # return an array of cell types
        base_color_land = [139, 69, 19] 
        base_color_water = [65, 105, 225]
        grid_rgb[cell_types == 'land'] = base_color_land
        grid_rgb[cell_types == "water"] = base_color_water

        land_mask = (cell_types == 'land')
        water_mask = (cell_types == 'water')
        gradient_land = np.zeros((grid.shape[0], grid.shape[1]), dtype=np.float32)
        gradient_water = np.zeros((grid.shape[0], grid.shape[1]), dtype=np.float32)
        gradient_land[land_mask] = 1.0 # setting the land cells to 1
        gradient_water[water_mask] = 1.0 # setting the water cells to 1

        self.apply_filter(gradient_land, base_color_land, land_mask, grid_rgb)
        self.apply_filter(gradient_water, base_color_water, water_mask, grid_rgb)
        
        # creating the images of the maps
        if save and seed is not None:
            filepath = f"{self.MAP_PATHS}//map_random_seed_{seed}.png"
        
            if not os.path.exists(filepath):
                img = Image.fromarray(grid_rgb)
                img.save(filepath)
        
        return grid_rgb
    
    def apply_filter(self, gradient_arr, base_color, mask, grid_rgb):
        """
        Function to apply a gaussian filter to the gradient array and then apply the color to the grid
        using the mask
        The filter will be applied by convolving the smooth gradient array with the base color
        to simulate a smooth change in the colors in the map
        """
        smooth_gradient_land = gaussian_filter(gradient_arr, sigma=1.5)
        smooth_color_land = np.array(base_color) * smooth_gradient_land[..., np.newaxis]
        grid_rgb[mask] = np.clip(smooth_color_land[mask], 0, 255).astype(np.uint8)

    def start(self):
        """
        This function initializes the animation and starts it
        """
        if self.ani is None:
            self.currentDay = 0
            if self.currentDay == 0:
                self.img = self.display_initial_setup() # function for displaying the initial setup
                plt.pause(1)
            # self.img = self.ax_plot.imshow(self.grid, interpolation='nearest')
            self.ani = FuncAnimation(self._fig_map, self.update, frames=list(range(1, self.maxDay + 1)), fargs=(self.img,),
                                interval=self.interval_val,
                                blit=False,
                                repeat=False,
                                cache_frame_data=False)
        else:
            self.ani.event_source.start()
        self.anim_running = True
        plt.show()

    def display_initial_setup(self):
        """
        Function to display the initial setup of the simulation
        """
        initial_grid = self.grid
        for artist in self.alive_animal_artists.values():
            artist.remove()
        
        self.alive_animal_artists.clear() # be sure that this dictionary is empty

        self.img = self.ax_plot.imshow(initial_grid, interpolation='nearest')
        self.draw_elements(initial_grid, day=0)
        self.day_text.set_text(f'Day 0')

        # plt.pause(0.1)
        return self.img

    def pause_animation(self):
        """
        Function to pause the animation
        """
        if self.anim_running:
            self.ani.event_source.stop()
            self.anim_running = False
        else:
            print("Animation is already paused")
            self.anim_running = False
    
    def faster_animation(self):
        """
        Function to speed up the animation by decreasing the interval of the animation
        """
        if self.anim_running:
            self.ani.event_source.stop()
            self.interval_val = 1
            self.ani.event_source.interval = self.interval_val
            self.ani.event_source.start()
            self.faster = True
    
    def normal_animation(self):
        """
        Function to revert the animation to the normal speed
        """
        if self.faster:
            self.ani.event_source.stop()
            self.interval_val = 2000
            self.ani.event_source.interval = self.interval_val
            self.ani.event_source.start()
            self.faster = False

    def show_cell_info(self, x, y):
        """
        Function that gets called after a cell is clicked
        shows the information of the cell in a new window
        """
        cell = self.env.getGrid()[x, y]
        fig = plt.figure(figsize=(8, 8), dpi=100)
        gs = GridSpec(2, 2, height_ratios=[3, 1], figure=fig)
        ax_img = fig.add_subplot(gs[0, 0])
        extent = [0, 1, 0, 1]
        
        if isinstance(cell, WaterCell):
            print("Water cell clicked")
            img_water = Image.open("files//water.png")
            ax_img.imshow(img_water)
            ax_img.set_title(f"Water Cell Clicled\nCell's coordinates: {x}, {y}", loc='center', weight='bold', fontsize=12)
            ax_img.axis('off')
            return
        # Showing the vegetob density of the cell
        cell_density = cell.getVegetobDensity()
        img_cell = self._get_vegetob_image(cell_density)
        ax_img.imshow(img_cell, extent=extent)
        ax_img.text(0.01, -0.45, f"Cell's coordinates: {x}, {y}", ha='left')
        ax_img.text(0.01, -0.35, f"Cell's vegetob density: {cell.getVegetobDensity()}")
        ax_img.axis('off')
        
        # Getting the animals in the cell
        erbast_list = cell.getErbastList()
        carviz_list = cell.getCarvizList()
        dead_list = cell.getDeadCreaturesList()
        if dead_list:
            # print("There are dead animals in the cell")
            tot_dead = len(dead_list)
            dead_empty = False
        else:
            # print("There are no dead animals in the cell")
            tot_dead = 1
            dead_empty = True
        if erbast_list:
            tot_erbast = len(erbast_list)
            erbast_empty = False
        else:
            # print("There are no erbasts in the cell")
            tot_erbast =  1
            erbast_empty = True
        if carviz_list:
            tot_carviz = len(carviz_list)
            carviz_empty = False
        else:
            # print("There are no carviz in the cell")
            tot_carviz = 1
            carviz_empty = True
        print(f"Amount of erbasts in cell {x, y}= {erbast_list} sum {tot_erbast}")
        print(f"Amount of erbasts in cell {x, y}= {carviz_list} sum {tot_carviz}")
        # Getting the total amount of rows for the grid
        total_rows = tot_erbast + tot_carviz + tot_dead + 3
        height_ratios = [0.1 for _ in range(total_rows)]
        gs_animals = GridSpec(total_rows, 1, figure=fig, height_ratios=height_ratios, width_ratios=[0.1], left=0.7, right=0.95, top=0.9, bottom=0.1) 
        
        axis_erbast = self.axis_individuals(tot_erbast, fig, gs_animals, 0, erbast=True, carviz=False, list_animals= erbast_list, empty=erbast_empty, dead_empty=dead_empty)
        axis_carviz = self.axis_individuals(tot_carviz, fig, gs_animals, tot_erbast+1, erbast=False, carviz=True, list_animals = carviz_list, empty=carviz_empty, dead_empty=dead_empty)
        axis_dead = self.axis_individuals(tot_dead, fig, gs_animals, tot_erbast+tot_carviz+2, erbast=False, carviz=False, list_animals = dead_list, empty=dead_empty, dead_empty=dead_empty)   
        
        # print("erbast axis", axis_erbast)
        # print("carviz axis", axis_carviz)
        self.individuals_axis = axis_erbast + axis_carviz + axis_dead # list with all the axis

        fig.canvas.draw()
        fig.show()
        # connecting the event of clicking on the axis to the function that will show the individual's information
        fig.canvas.mpl_connect('button_press_event', lambda event: self.track_onclick(event, self.individuals_axis))
    
    def axis_individuals(self, n : int, fig, gs, start_row, erbast : bool, carviz : bool, list_animals : list, empty : bool, dead_empty : bool):
        """
        This function will create the axis for the individuals in the cell and display 
        the individual's id or a message if there are no individuals in the cell
            - n: number of individuals in the cell
            - fig: the figure where the axis will be created
            - gs: the grid specification of the figure
            - start_row: the row where the axis will start
            - erbast: boolean to know if the individuals are erbasts
            - carviz: boolean to know if the individuals are carviz
            - list_animals: list of the individuals in the cell
            - empty: boolean to know if the cell is empty
            - dead_empty: boolean to know if there are dead animals in the cell
        """
        title_pos = start_row
        ax_title = fig.add_subplot(gs[title_pos, 0])
        if erbast:
            t = f"Erbast in cell"
        elif carviz:
            t = f"Carviz in cell"
        else:
            t = f"Dead animals in cell"
        ax_title.text(0.3, 0.3, t, ha='center', fontsize=12)
        ax_title.axis('off')

        if erbast and empty:
            s_empty = 'There are no Erbast in cell'
        elif carviz and empty:
            s_empty = 'There are no Carviz in cell'
        elif not erbast and not carviz and dead_empty:
            s_empty = 'There are no dead animals in cell'
        else:
            s_empty = 'No animals in this category'
        
        individuals_axis = [] # creating a list to store the axis
        for i in range(n):
            ax = fig.add_subplot(gs[start_row + 1 + i, 0])
            if empty:
                ax.text(0.3, 0.3, f"{s_empty}", ha='center', 
                        fontsize=8, bbox=dict(facecolor=self.AXES_COLOR, edgecolor='black', boxstyle='round'))
                individuals_axis.append((ax, None))
            else:
                animal = list_animals[i]
                if isinstance(animal, Erbast):
                    s = f"Erbast{str(animal.id)}" # getting the animal's id
                elif isinstance(animal, Carviz):
                    s = f"Carviz{str(animal.id)}"
                else:
                    s = f"Dead animal {str(animal.old_species)}{str(animal.id)}"
                ax.text(0.3, 0.2, f"{s}", ha='center', 
                        fontsize=8, bbox=dict(facecolor=self.AXES_COLOR, edgecolor='black', boxstyle='round'))
                individuals_axis.append((ax, list_animals[i]))

            ax.axis('off')

        fig.canvas.draw()
        return individuals_axis
    
    def track_onclick(self, event, individuals_axis):
        """
        Function to track which axis was clicked and show the individual's information
        on a new window
        """
        for i, (ax, individual) in enumerate(individuals_axis):
            if ax == event.inaxes and individual is not None:
                self.show_individuals(individual)
                break # after the axis is found break the loop

    def show_individuals(self, clicked_individual):
        """
        This function will display individual's information that was clicked in a new figure
        """
        dead_creature = False # tracking whether the information to be displayed is from a dead animal
        
        fig = plt.figure(figsize=(5,5), dpi=100)
        gs_stats = GridSpec(5, 2, figure=fig, 
                        width_ratios=[1, 1], 
                        height_ratios=[0.4, 0.4, 0.4, 0.2, 0.2], 
                        left=0.05, right=0.95, top=0.9, bottom=0.1)
        
        # creating all the subplots for the information
        if isinstance(clicked_individual, DeadCreature):
            clicked_individual = clicked_individual.deadAnimal # accessing the old animal of the dead creature
            dead_creature = True
        self.create_animal_subplot(fig, gs_stats, clicked_individual, dead_creature)
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
        ax_info.text(0.5, 0.015, social_group, 
                    fontsize=8, ha='center', va='center', transform=ax_info.transAxes)
        status = "Alive" if clicked_individual.alive else "Dead"
        ax_info.text(0.5, -0.4, f"Status: {status}", 
                    fontsize=8, ha='center', va='center', transform=ax_info.transAxes)
        ax_info.axis('off')
        
        fig.subplots_adjust(hspace=0.7)
        fig.show()

    def create_animal_subplot(self, fig, gs_stats, clicked_individual, dead_creature=False):
        """
        Create subplot for animal image.
        If dead_creature is True, the image will be of a dead animal
        """
        ax_animal = fig.add_subplot(gs_stats[0:2, 0])
        if dead_creature:
            animal_path = "files//erbast_dead.png" if isinstance(clicked_individual, Erbast) else "files//carviz_dead.png"
        else:
            animal_path = "files//carvizN.jpg" if isinstance(clicked_individual, Carviz) else "files//erbastN.jpg"
        animal_art = Image.open(animal_path)
        ax_animal.imshow(animal_art, extent=[0.0, 1.0, 0.0, 1.0])
        ax_animal.text(0.5, -0.1, f"Individual's ID: {clicked_individual.id} ", 
                    fontsize=8, ha='center', va='center', transform=ax_animal.transAxes)
        ax_animal.axis('off')
        return ax_animal
    
    def create_age_subplot(self, fig, gs_stats, individual_age):
        """
        Creating the subplot for the age
        """
        ax_age = fig.add_subplot(gs_stats[1, 1])
        heart = Image.open("files//heart_png.png")
        ax_age.imshow(heart)
        ax_age.text(1.0, 0.5, f'Age: {individual_age}', fontsize=8, ha='left', va='center', transform=ax_age.transAxes)
        ax_age.axis('off')
        return ax_age

    def create_social_att_subplot(self, fig, gs_stats, individual_att):
        """
        Creating the subplot for the social attitude
        """
        att_path = self._get_social_att_image(individual_att)
        ax_social_att = fig.add_subplot(gs_stats[2, 1])
        socialAtt = Image.open(att_path).resize((2000, 700))
        ax_social_att.imshow(socialAtt)
        ax_social_att.text(0.3, -0.1, f'Social ATT: {individual_att:.2f}', fontsize=8, ha='left', va='center', transform=ax_social_att.transAxes)
        ax_social_att.axis('off')
        return ax_social_att
    
    def _get_social_att_image(self, attitude):
        """
        Function to get the image of the social att based on its value
        """
        if attitude == 0:
            return self.IMAGE_PATHS['SOCIAL_ATT']['ZERO']
        elif attitude < 30:
            return self.IMAGE_PATHS['SOCIAL_ATT']['LOW']
        elif attitude < 100:
            return self.IMAGE_PATHS['SOCIAL_ATT']['MEDIUM']
        return self.IMAGE_PATHS['SOCIAL_ATT']['HIGH']
    

    def create_energy_subplot(self, fig, gs_stats, individual_energy):
        """
        Creating the subplot for the energy
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
        Function to get the image of the energy based on its value
        """
        if energy == 0:
            return self.IMAGE_PATHS['ENERGY']['ZERO']
        elif energy < 30:
            return self.IMAGE_PATHS['ENERGY']['LOW']
        elif energy < 100:
            return self.IMAGE_PATHS['ENERGY']['MEDIUM']
        return self.IMAGE_PATHS['ENERGY']['HIGH']
    
    def _get_vegetob_image(self, cell_density):
        """
        Function to get the image for the cell based on its vegetob density
        """
        if cell_density < 25:
            img_cell = Image.open(self.IMAGE_PATHS['CELL']['DIRT'])
        elif 25 < cell_density < 50:
            img_cell = Image.open(self.IMAGE_PATHS['CELL']['GRASS_LOW'])
        elif 50 < cell_density < 100:
            img_cell = Image.open(self.IMAGE_PATHS['CELL']['GRASS_MED'])
        else:
            img_cell = Image.open(self.IMAGE_PATHS['CELL']['GRASS_HIGH'])
        
        return img_cell




