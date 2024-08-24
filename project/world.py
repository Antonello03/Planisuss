import random
from planisuss_constants import *
import numpy as np

ON = 255
OFF = 0

def randomize(gridEL, percentage=0.5):
    ''' Stupid fucntion tu generate ranom initial population'''

    if random.random()<percentage:
        return 255
    else:
        return 0
v_randomize = np.vectorize(randomize)

class Environment ():
    """
    The Environment class is the core of Planisuss world.
    Each living being is contained here and the inizialization
    and update logic of the world is is managed by the following functions
    """

    def __init__(self):
        self.grid = np.zeros(shape=(NUMCELLS,NUMCELLS))
        self.grid = v_randomize(self.grid, 0.3)
        print(self.grid)

    def getEnv(self):
        print(len(self.grid))
        return self.grid
    
    def updateEnv(self):
        N = NUMCELLS
        
        newGrid = self.grid.copy()
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

        self.grid = newGrid
        return self.grid