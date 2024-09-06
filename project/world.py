import random
from creatures import Vegetob, Erbast, Carviz, Animal, SocialGroup, Herd, Pride
from planisuss_constants import *
from typing import Union
import numpy as np
import noise


# TODO should erbasts still be assigned to a cell or should the herd be assigned and the erbast retrieved trough it? How will this affect animals being able to see each others?

ON = 255
OFF = 0

class Environment(): # TODO - modify move animals to allow for group momvements
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
      
    def getHerds(self) -> list[Herd]:
        """Obtain all herds in environments"""
        herds = set()
        for erb in self.creatures["Erbast"]:
            socG = erb.getSocialGroup()
            if socG is not None:
                herds.add(socG)
        return list(herds)

    def getAloneErbasts(self) -> list[Erbast]:
        return [e for e in self.creatures["Erbast"] if e.inSocialGroup == False]

    def updateGrid(self, newGrid):
        self.world.updateGrid(newGrid)

    def add(self, object:Union[Animal, SocialGroup]):
        """
        Adds an Animal or a SocialGroup to the environment.
        This allows the environment to correctly assign and monitor the new individuals
        and it is fundamental for the correct functioning of the simulation
        """
        if isinstance(object, Animal):
            self.addAnimal(object)
        elif isinstance(object, SocialGroup):
            self.addGroup(object)
        else:
            raise Exception(f"Given object ({object}) must be either an Animal or a SocialGroup")
        return True

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
        x,y = group.getCoords()

        if isinstance(group, Herd):
            self.creatures["Erbast"].extend(group.getComponents())
            self.getGrid()[x][y].addGroup(group)
            self.totErbast += group.numComponents

        if isinstance(group, Pride):
            self.creatures["Carviz"].extend(group.getComponents())
            self.getGrid()[x][y].addGroup(group)
            self.totCarviz += group.numComponents    

    def remove(self, object:Union[Animal, SocialGroup]):
        if isinstance(object, Animal):
            self.removeAnimal(object)
        elif isinstance(object, SocialGroup):
            self.removeGroup(object)
        else:
            raise Exception(f"Given object ({object}) must be either an Animal or a SocialGroup")
        return True

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
                                                                
    def removeGroup(self, group:SocialGroup): # TODO write code for pride while checking from removeAnimal
        """"""
        if not isinstance(group, SocialGroup):
            raise TypeError(f"{group} is not a social Group")
        
        x,y = group.getCoords()

        if isinstance(group, Herd):
            if all(el in self.creatures["Erbast"] for el in group.getComponents()):
                self.totErbast -= group.numComponents
                self.getGrid()[x][y].removeHerd()
                self.creatures["Erbast"] = [erb for erb in self.creatures["Erbast"] if erb not in group.getComponents()]

    def move(self, object:Union[list[Animal], list[SocialGroup]], newCoords:list[tuple]): #TODO can make this work with a list of both anim and social
        """moves animals or socialgroups to newCoords, eventually changing their attributes"""
        if all(isinstance(o, Animal) for o in object):
            self.moveAnimals(object, newCoords)
        elif all(isinstance(o, SocialGroup) for o in object):
            self.moveGroups(object, newCoords)

    def moveAnimals(self, animals:list[Animal], newCoords:list[tuple]):
        """given new coords, move all the animals if possible and change its coords"""

        for a in animals:
            if not isinstance(a, Animal):
                raise TypeError(f"{a} is not an Animal")

        animals = animals[:] # very important step...
        for animal in animals:
            self.removeAnimal(animal)
        for animal, newCoord in zip(animals, newCoords):
            animal.coords = newCoord
        for animal in animals[:]:
            self.addAnimal(animal)

    def moveGroups(self, groups:list[SocialGroup], newCoords:list[tuple]):
        """moves a socialGroup from a cell to another updating eventually the interested parameters"""
        for g in groups:
            if not isinstance(g, SocialGroup):
                raise TypeError(f"{g} is not a SocialGroup")
        
        groups = groups[:]
        for g in groups:
            self.removeGroup(g)
        for g, newCoord in zip(groups, newCoords):
            g.coords = newCoord
            for animal in g.components:
                animal.coords = newCoord
        for g in groups:
            self.addGroup(g)

    def nextDay(self):
        """The days phase happens one after the other until the new day"""

        grid = self.getGrid()
        cells = grid.reshape(-1)
        landCells = [landC for landC in cells if isinstance(landC,LandCell)]
        # 1 - GROWING
        for el in landCells:
            el.growVegetob()

        # 2 MOVING

        # Erbast move - TODO - the following logic will be modified in order to add herds and prides
        nextCellCoords = []
        erbastsToMove = self.creatures["Erbast"]

        for erbast in erbastsToMove:
            nextCoords_tmp = erbast.rankMoves(grid)[0][1]
            nextCellCoords.append(nextCoords_tmp) # take best choice coords TODO- at the end the logic will be more complex
            print(f"{erbast} is in {erbast.getCoords()} and wants to move in {nextCoords_tmp} which is a {grid[nextCoords_tmp]}")
            
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
        return f"Cell {self.coords}"

class WaterCell(Cell):
    """
    WaterCells can't contain living being... for now...
    """

    def __init__(self, coordinates:tuple):
        super().__init__(coordinates = coordinates)

    def getCellType(self):
        return "water"
    
    def __repr__(self):
        return f"WaterCell {self.coords}"
    
class LandCell(Cell):
    """
    LandCells host life
    """

    def __init__(self, coordinates:tuple, vegetobPopulation: Vegetob):
        super().__init__(coordinates = coordinates)
        self.vegetob = vegetobPopulation
        self.creatures = {
            "Erbast" : [],
            "Carviz" : []
        }
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
        if isinstance(animal, Erbast):
            if self.numErbast == 0:
                self.creatures["Erbast"].append(animal)
                self.numErbast += 1
            elif self.numErbast == 1: # add in Herd
                presentAnimal = self.creatures["Erbast"][0]
                herd = Herd([presentAnimal, animal])
                self.removeAnimal(presentAnimal)
                self.addGroup(herd)
            elif self.numErbast > 1 :
                self.creatures["Erbast"].append(animal)
                self.numErbast += 1
                self.herd.addComponent(animal)

        if isinstance(animal, Carviz): #TODO Carviz logic
            if self.pride is None:
                self.creatures["Carviz"].append(animal)
                self.numCarviz += 1

    def removeAnimal(self, animal:'Animal'):
        """Remove an animal from the inhabitants list"""
        if isinstance(animal, Erbast):
            if animal in self.creatures["Erbast"]:
                if self.numErbast <= 1:
                    self.numErbast -= 1
                    self.creatures["Erbast"].remove(animal)
                elif self.numErbast == 2:
                    presentHerd = self.herd.getComponents()
                    presentHerd.remove(animal)
                    remainingAnimal = presentHerd[0]
                    remainingAnimal.inSocialGroup = False
                    remainingAnimal.socialGroup = None
                    self.removeHerd()
                    self.addAnimal(remainingAnimal)
                else: 
                    self.creatures["Erbast"].remove(animal)
                    self.numErbast -= 1
                    self.herd.loseComponent(animal)
            else:
                raise Exception(f"{animal} is not a creature of the cell: {self}, hence it can't be removed")

        elif isinstance(animal, Carviz):
            if animal in self.creatures["Carviz"]:
                self.creatures["Carviz"].remove(animal)
                self.numCarviz -= 1

    def addGroup(self, group:'SocialGroup'):
        """
        add a Herd or a Pride to the landCell and eventually resolve conflicts / join groups
        """
        if isinstance(group, Herd):
            if self.herd is not None:
                self.herd.joinGroups(group)
                self.creatures["Erbast"].extend(group.getComponents())
                self.numErbast += group.numComponents
                pass
            else:
                if self.numErbast == 1:
                    presentAnimal = self.creatures["Erbast"][0]
                    self.removeAnimal(presentAnimal)
                    group.addComponent(presentAnimal)
                self.herd = group
                self.creatures["Erbast"].extend(group.getComponents())
                self.numErbast += group.numComponents
                

        elif isinstance(group, Pride):
            if self.pride is not None:
                #TODO - join prides / struggle
                pass
            else:
                self.pride = group
                self.creatures["Carviz"].extend(group.getComponents())
                self.numCarviz += group.numComponents

    def removeHerd(self):
        """Remove the herd from the landCell"""
        if self.herd is not None:
            self.herd = None
            self.creatures["Erbast"] = []
            self.numErbast = 0

    def removePride(self): # TODO multiple prides could co-exist i think
        """Remove the pride from the landCell"""
        if self.pride is not None:
            self.pride = None
            self.creatures["Carviz"] = [] 
            self.numCarviz -= self.pride.numComponents

    def getErbastList(self):
        """Get a list of all Erbast inhabitants in the cell"""
        return [erb for erb in self.inhabitants if isinstance(erb, Erbast)]

    def getCarvizList(self):
        """Get a list of all Carviz inhabitants in the cell"""
        return [car for car in self.inhabitants if isinstance(car, Carviz)]

    def getCellType(self):
        return "land"

    def getHerd(self):
        return self.herd
    
    def getPride(self):
        return self.pride
    
    def __repr__(self):
        return f"LandCell {self.coords}"
    
