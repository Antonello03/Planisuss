import random
from planisuss_constants import *
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
    class that handles the creation of the islands, initial flora and fauna, and aquatic zones

    its main attribute is grid
    """
    def randomGrid(self, gridEL, percentage=0.5):
        ''' Stupid fucntion tu generate ranom initial population'''
        if random.random() < percentage:
            return 255
        else:
            return 0
    v_randomGrid = np.vectorize(randomGrid)

    def __fbmNoise(self, n, threshold = 0.4, seed = None, octaves=8, persistence=0.4, lacunarity=1.8, scale=40.0):
        """ Method to generate island like maps """
        if seed is None:
            seed = random.randint(0, 100)
        grid = np.zeros((n, n))
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
        print(grid)
        grid = np.where(grid > threshold, 255, 0)
        print(grid)
        
        return grid

    def __init__(self, type = "fbm"):
        self.grid = self.createWorld(type)
        
    # so that we can crate different types of initial setups
    def createWorld(self, typology = "fbm"):
        if typology == "random":
            grid = np.zeros(shape=(NUMCELLS,NUMCELLS))
            grid = self.v_randomGrid(self.grid, 0.3)
            return grid
        
        if typology == "fbm":
            grid = self.__fbmNoise(NUMCELLS)
            return grid

        if typology == "type2":
            pass

    def updateGrid(self, newGrid):
        self.grid = newGrid