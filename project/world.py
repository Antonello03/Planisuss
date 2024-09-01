import random
from creatures import Vegetob, Erbast, Carviz, Animal, SocialGroup
from planisuss_constants import *
import numpy as np
import noise


# TODO should erbasts still be assigned to a cell or should the herd be assigned and the erbast retrieved trough it? How will this affect animals being able to see each others?

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
        self.creatures = {
            "Erbast" : [],
            "Carviz" : []
        }
        self.totErbast = 0
        self.totCarviz = 0

    def getGrid(self) -> 'WorldGrid':
        return self.world.grid
    
    def updateGrid(self, newGrid):
        self.world.updateGrid(newGrid)

    def addAnimal(self, animal:Animal):

        """
        My approach where each landCell know its inhabitants,
        each creature know its coordinates and the whole environment knows everything
        need a bit more care when managing inhabitants
        """
        if not isinstance(animal, Animal):
            raise TypeError(f"{animal} is not an Animal")
        
        x,y = animal.getCoords()

        if isinstance(animal, Erbast):
            self.creatures["Erbast"].append(animal) # add to env
            self.getGrid()[x][y].addAnimal(animal) # add to cell
            self.totErbast += 1

        elif isinstance(animal, Carviz):
            self.creatures["Carviz"].append(animal)
            self.getGrid()[x][y].addAnimal(animal)
            self.totCarviz += 1

    def addGroup(self, group:SocialGroup):
        pass

    def removeAnimal(self, animal:Animal):
        """Remove an animal from the creatures list"""

        if not isinstance(animal, Animal):
            raise TypeError(f"{animal} is not an Animal")
        
        x,y = animal.getCoords()

        if isinstance(animal, Erbast):
            if animal in self.creatures["Erbast"]:
                self.getGrid()[x][y].removeAnimal(animal)
                self.creatures["Erbast"].remove(animal)
                self.totErbast -= 1
                return True
            
        elif isinstance(animal, Carviz):
            if animal in self.creatures["Carviz"]:
                self.getGrid()[x][y].removeAnimal(animal)
                self.creatures["Carviz"].remove(animal)
                self.totCarviz -= 1
                return True
            
        raise Exception(f"animal: {animal}, at coords {animal.getCoords()}, is not present in any cell or is not a Erbast/Carviz")

    def moveAnimal(self, animal:Animal, newCoords:tuple): # DON'T USE FOR MULTIPLE ANIMALS
        """given new coords, move the animal if possible and change its coords"""
        if not isinstance(animal, Animal):
            raise TypeError(f"{animal} is not an Animal")

        self.removeAnimal(animal)
        animal.coords = newCoords
        self.addAnimal(animal)

    def moveAnimals(self, animals:list[Animal], newCoords:list[tuple]):

        animals = animals[:] # very important step...
        for animal in animals:
            self.removeAnimal(animal)
        for animal, newCoord in zip(animals, newCoords):
            animal.coords = newCoord
        for animal in animals[:]:
            self.addAnimal(animal)

    def nextDay(self):
        """The days phase happens one after the other until the new day"""

        grid = self.getGrid()
        cells = grid.reshape(-1)
        landCells = [landC for landC in cells if isinstance(landC,LandCell)]
        # 1 - GROWING
        for el in landCells:
            el.growVegetob()

        # 2 MOVING

        # Erbast move - the following logic will be modified in order to add herds and prides
        nextCellCoords = []
        erbastsToMove = self.creatures["Erbast"]

        for erbast in erbastsToMove:
            nextCellCoords.append(erbast.rankMoves(grid)[0][1]) # take best choice coords TODO- at the end the logic will be more complex
        self.moveAnimals(erbastsToMove,nextCellCoords)

        return self.getGrid()
    
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
            values_grid = self.__fbmNoise(NUMCELLS, threshold, dynamic=True)
            grid = np.zeros((NUMCELLS, NUMCELLS), dtype=object)
            for i in range(NUMCELLS):
                for j in range(NUMCELLS):
                    if values_grid[i][j] > threshold:
                        grid[i][j] = LandCell((i, j), Vegetob(density=25 + random.randint(-10, 10)))
                    else:
                        grid[i][j] = WaterCell((i, j))
            return grid

    def updateGrid(self, newGrid):
        self.grid = newGrid

class Cell():
    """
    Each Grid unit is a cell. Cells contain several information about
    the species that habits it, the amount of vegetation and so on
    """

    def __init__(self, coordinates:tuple):
        self.coords = coordinates
        pass

    def getCoords(self):
        return self.coords

    def getCellType(self):
        pass

    def __repr__(self):
        return "Cell"

class WaterCell(Cell):
    """
    WaterCells can't contain living being... for now...
    """

    def __init__(self, coordinates:tuple):
        super().__init__(coordinates = coordinates)

    def getCellType(self):
        return "water"
    
    def __repr__(self):
        return "WaterCell"
    
class LandCell(Cell):
    """
    LandCells host life
    """

    def __init__(self, coordinates:tuple, vegetobPopulation: Vegetob):
        super().__init__(coordinates = coordinates)
        self.vegetob = vegetobPopulation
        self.inhabitants = list()
        self.herd = None
        self.pride = None
        self.numErbast = 0
        self.numCarviz = 0

    def getVegetobDensity(self):
        """Get Vegetob Density in the cell"""
        return self.vegetob.density
    
    def growVegetob(self, times:int = 1):
        """Grow the Vegetob population in the cell"""
        self.vegetob.grow(times)

    def reduceVegetob(self, amount:int = 5):
        """apply grazing effects on the Vegetob population in the cell"""
        self.vegetob.reduce(amount)

    def addAnimal(self, animal:'Animal'):
        """add an animal from the inhabitants list"""
        # TODO
        # to add limitation on the amount of erbaz/carviz
        # to add joining herd dynamics
        self.inhabitants.append(animal)
        if isinstance(animal, Erbast):
            self.numErbast += 1
        elif isinstance(animal, Carviz):
            self.numCarviz += 1

    def removeAnimal(self, animal:'Animal'):
        """Remove an animal from the inhabitants list"""
        if animal in self.inhabitants:
            self.inhabitants.remove(animal)
            if isinstance(animal, Erbast):
                self.numErbast -= 1
            elif isinstance(animal, Carviz):
                self.numCarviz -= 1

    def addGroup(self, group:'SocialGroup'):
        """
        add a Herd or a Pride to the landCell and eventually resolve conflicts / join groups
        """
        if isinstance(group, 'Herd'):
            if self.herd is not None:
                #TODO - join the two herds
                pass
            else:
                self.herd = group
                self.numErbast += group.numComponents

        elif isinstance(group, 'Pride'):
            if self.pride is not None:
                #TODO - join prides / struggle
                pass
            else:
                self.pride = group
                self.numCarviz += group.numComponents

    def removeHerd(self):
        """Remove the herd from the landCell"""
        if self.herd is not None:
            self.herd = None
            self.numErbast -= self.herd.numComponents

    def removePride(self):
        """Remove the pride from the landCell"""
        if self.pride is not None:
            self.pride = None
            self.numCarviz -= self.pride.numComponents

#    def removeGroup(self, ):


    def getErbastList(self):
        """Get a list of all Erbast inhabitants in the cell"""
        return [erb for erb in self.inhabitants if isinstance(erb, Erbast)]

    def getCarvizList(self):
        """Get a list of all Carviz inhabitants in the cell"""
        return [car for car in self.inhabitants if isinstance(car, Carviz)]

    def getCellType(self):
        return "land"
    
    def __repr__(self):
        return "LandCell"
    
