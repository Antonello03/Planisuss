import random
from planisuss_constants import *
from creatures import *
import numpy as np
import noise

ON = 255
OFF = 0

class Environment():
    """
    The Environment class is the core of Planisuss world.
    Each living being and the worldGrid itself is contained here and the inizialization
    and update logic of the world is managed by the following functions
    """
    def __init__(self):
        self.world = WorldGrid()
        self.grid = self.world.grid #redundancy to be removed

    def getGrid(self):
        return self.world.grid
    
    def updateEnv(self):
        N = NUMCELLS
        # Evolution of the world logic
        newGrid = self.world.grid.copy()
        for i in range(N):
            for j in range(N):
                total = int((self.grid[i, (j-1)%N] + self.grid[i, (j+1)%N] +
                            self.grid[(i-1)%N, j] + self.grid[(i+1)%N, j] +
                            self.grid[(i-1)%N, (j-1)%N] + self.grid[(i-1)%N, (j+1)%N] +
                            self.grid[(i+1)%N, (j-1)%N] + self.grid[(i+1)%N, (j+1)%N]) / 255)
                if self.grid[i, j]  == ON:
                    if (total < 2) or (total > 3):
                        newGrid[i, j] = OFF
                else:
                    if total == 3:
                        newGrid[i, j] = ON

        # Updating the WorldGrid
        self.world.updateGrid(newGrid)
        self.grid = self.world.grid #redundancy to be removed
        return self.world.grid
    
class WorldGrid():
    """
    class that handles the creation of the islands, initial flora and fauna,
    and aquatic zones its main attribute is grid
    """
    def __fbmNoise(self, n, threshold = 0.2, seed = None, octaves=8, persistence=0.4, lacunarity=1.8, scale=40.0, dynamic=False):
        """ Method to generate island like maps. Returns a numpy grid of zeros and 255 """
        if seed is None:
            seed = random.randint(0, 100)
        grid = np.zeros((n, n))
        center = n // 2
        max_dist = center * np.sqrt(2)
        for i in range(n):
            for j in range(n):
                x = i / scale
                y = j / scale
                fbm_value = 0.0
                amplitude = 1.0
                frequency = 1.0
                for _ in range(octaves):
                    fbm_value += amplitude * noise.pnoise2(x * frequency, y * frequency, base = seed)
                    amplitude *= persistence
                    frequency *= lacunarity

                grid[i][j] = fbm_value

        # Normalize the values between 0 and 1
        min_val = np.min(grid)
        max_val = np.max(grid)
        grid = (grid - min_val) / (max_val - min_val)

        if dynamic:
          for i in range(n):
              for j in range(n):
                  distance = np.sqrt((i - center) ** 2 + (j - center) ** 2)
                  distance_weight = distance / max_dist
                  dynamic_treshold = threshold + (1 - threshold) * distance_weight
                  # print(dynamic_treshold)
                  grid[i][j] = 1 if grid[i][j] > dynamic_treshold else 0
        else:
          grid = np.where(grid > threshold, 1, 0)
        return grid

    def __init__(self, type = "fbm", threshold = 0.2):
        self.grid = self.createWorld(type, threshold)

    # so that we can crate different types of initial setups
    def createWorld(self, typology = "fbm", threshold = 0.2):
        """
        Initialize the world
        Vegetob density starts at 26
        """
        
        if typology == "fbm":
            grid = self.__fbmNoise(NUMCELLS, threshold, dynamic=True)
            grid = np.where(grid > threshold, LandCell(Vegetob(density = 25)), WaterCelL())
            return grid

    def updateGrid(self, newGrid):
        self.grid = newGrid

class Cell():
    """
    Each Grid unit is a cell. Cells contain several information about
    the species that habits it, the amount of vegetation and so on
    """

    def __init__(self):
        pass

    def getCellType(self):
        pass

    def __repr__(self):
        return "Cell"

class WaterCelL(Cell):
    """
    WaterCells can't contain living being... for now...
    """

    def __init__(self):
        super().__init__()

    def getCellType(self):
        return "water"
    
    def __repr__(self):
        return "WaterCell"
    
class LandCell(Cell):
    """
    LandCells host life
    """

    def __init__(self, vegetobPopulation: Vegetob):
        super().__init__()
        self.vegetob = vegetobPopulation

    def getVegetobDensity(self):
        """Get Vegetob Density in the cell"""
        return self.vegetob.density
    
    def growVegetob(self, times:int = 1):
        """Grow the Vegetob population in the cell"""
        self.vegetob.grow(times)

    def reduceVegetob(self, amount:int = 5):
        """apply grazing effects on the Vegetob population in the cell"""
        self.vegetob.reduce(amount)

    def getCellType(self):
        return "land"
    
    def __repr__(self):
        return "LandCell"
    
