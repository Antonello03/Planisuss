import random
from planisuss_constants import *
import numpy as np

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
    def randomGrid(gridEL, percentage=0.5):
        ''' Stupid fucntion tu generate ranom initial population'''

        if random.random() < percentage:
            return 255
        else:
            return 0
    v_randomGrid = np.vectorize(randomGrid)

    def __init__(self, type = "islands"):
        self.grid = self.createWorld(type)
        
    # so that we can crate different types of initial setups
    def createWorld(self, typology = "islands"):
        if typology == "islands":
            self.grid = np.zeros(shape=(NUMCELLS,NUMCELLS))
            self.grid = self.v_randomGrid(self.grid, 0.3)
            return self.grid
        
        if typology == "type1":
            pass

        if typology == "type2":
            pass

    def updateGrid(self,newGrid):
        self.grid = newGrid