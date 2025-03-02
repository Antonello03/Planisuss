from collections import defaultdict
import random
from creatures import Vegetob, Erbast, Carviz, Animal, SocialGroup, Herd, Pride, Species, DeadCreature
from planisuss_constants import *
from typing import Union
import numpy as np
import noise

# TODO Carviz join dynamic and others...
# TODO groups should be smart enough to avoid going back to the same cell...

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
        self.deadCreatures = []
        self.totErbast = 0
        self.totCarviz = 0
        self.day = -1

    def getGrid(self) -> 'WorldGrid':
        return self.world.grid
      
    def getHerds(self) -> list[Herd]:
        """Obtain all herds in environment"""
        herds = set()
        for erb in self.creatures["Erbast"]:
            socG = erb.getSocialGroup()
            if socG is not None:
                herds.add(socG)
        return list(herds)
    
    def getPrides(self) -> list[Pride]:
        """Obtain all prides in environment"""
        prides = set()
        for carviz in self.creatures["Carviz"]:
            socG = carviz.getSocialGroup()
            if socG is not None:
                prides.add(socG)
        return list(prides)

    def getAloneErbasts(self) -> list[Erbast]:
        """Get a list of Erbast that are not in a social group"""
        return [e for e in self.creatures["Erbast"] if e.inSocialGroup == False]
    
    def getAloneCarviz(self) -> list[Carviz]:
        """Get a list of Carviz that are not in a social group"""
        return [c for c in self.creatures["Carviz"] if c.inSocialGroup == False]
    
    def getDeadCreatures(self) -> list[DeadCreature]:
        """Get list of DeadCreatures in the environment"""
        return self.deadCreatures

    def updateGrid(self, newGrid):
        self.world.updateGrid(newGrid)

    def add(self, object:Species):
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
            self.creatures["Erbast"].append(animal) 
            self.getGrid()[x][y].addAnimal(animal)
            self.totErbast += 1

        elif isinstance(animal, Carviz):
            self.creatures["Carviz"].append(animal)
            self.getGrid()[x][y].addAnimal(animal)
            self.totCarviz += 1

    def changeEnergyAndHandleDeath(self, species:Species, energy:int):
        """Change the energy of a social group or an Animal and handle the death of the individuals"""
        if isinstance(species, SocialGroup):
            aliveDict = species.changeEnergy(energy)
            for creature in aliveDict:
                if not aliveDict[creature]:
                    self.creatureDeath(creature)

            return all(aliveDict.values())
            

        elif isinstance(species, Animal):
            alive = species.changeEnergy(energy)
            if not alive:
                self.creatureDeath(species)
                return False

        return True

    def creatureDeath(self, animal:Animal):
        """Handles the death of a creature"""
        animal.die()
        self.addDeadCreature(DeadCreature(animal, self.day))
        self.remove(animal)

    def addDeadCreature(self, deadCreature:DeadCreature):
        self.deadCreatures.append(deadCreature)
        return self.deadCreatures

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

    def remove(self, object:Species):
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
                                                                
    def removeGroup(self, group:SocialGroup):
        """"""
        if not isinstance(group, SocialGroup):
            raise TypeError(f"{group} is not a social Group")
        
        x,y = group.getCoords()

        if isinstance(group, Herd):
            if all(el in self.creatures["Erbast"] for el in group.getComponents()):
                self.totErbast -= group.numComponents
                self.creatures["Erbast"] = [erb for erb in self.creatures["Erbast"] if erb not in group.getComponents()]
                self.getGrid()[x][y].removeHerd()

        elif isinstance(group, Pride):
            if all(el in self.creatures["Carviz"] for el in group.getComponents()):
                self.totCarviz -= group.numComponents
                self.creatures["Carviz"] = [carv for carv in self.creatures["Carviz"] if carv not in group.getComponents()]
                self.getGrid()[x][y].removePride(group)

    def move(self, nextCoords: dict[Species, tuple]):
        """
        Move animals or social groups to new coordinates.
        
        Args:
            nextCoords (dict[Species, tuple]): A dictionary where keys are objects to be moved, which can be either animals or social groups, and values are their new coordinates.
        
        Raises:
            TypeError: If any key in the 'nextCoords' dictionary is not an instance of Animal or SocialGroup.
        """
        if not all(isinstance(obj, Species) for obj in nextCoords.keys()):
            raise TypeError(f"can't move objects which are not animals or SocialGroups")
        
        objects = nextCoords.keys()
        
        for o in objects:
            self.remove(o)
        
        for o, c in nextCoords.items():
            self._changeCoords(o, c)
        
        for o in objects:
            self.add(o)
        
    def _changeCoords(self, obj:Species,newCoords:tuple):
        """helper func to changee the coords of an animal or a socialgroup"""
        if isinstance(obj, Animal):
            obj.coords = newCoords
            return True
        elif isinstance(obj, SocialGroup):
            for el in obj.getComponents():
                el.coords = newCoords
            obj.updateCoords(newCoords)
            return True
        else:
            raise TypeError(f"obj must be either Animal or SocialGroup, received {obj}")

    def graze(self, grazer:Union[Erbast,Herd]):
        """handles the grazing by calling erbast and cell methods"""
        grazingCoords = grazer.getCoords()
        grazingCell = self.getGrid()[grazingCoords]
        availableVegetobs = grazingCell.getVegetobDensity()
        grazedAmount = grazer.graze(availableVegetobs) # consume specified amount and update energy
        grazingCell.reduceVegetob(grazedAmount) # reduce vegetob density in cell

    def getCellSpeciesDict(self, species: list[Species]) -> dict[tuple,list[Species]]:
        """
        Given the interested Species, returns a dict where the keys are the coordinates of the cells and the values are the inhabitants
        """
        cellSpecies = defaultdict(list)
        for c in species:
            cellSpecies[c.getCoords()].append(c)

        return cellSpecies

    def joinCarvizesToPride(self):
        """
        Adds all the carviz that are in the same cell of a Pride to the pride with the highest socAttitude
        """

        cellSpecies = self.getCellSpeciesDict(self.getAloneCarviz() + self.getPrides())

        for coords in cellSpecies:
            mostSocialPride = None
            for pride in cellSpecies[coords]: # find best pride
                if isinstance(pride, Pride):
                    if not mostSocialPride:
                        mostSocialPride = pride
                    else:
                        if pride.getGroupSociality() > mostSocialPride.getGroupSociality():
                            mostSocialPride = pride

            if mostSocialPride:
                for carviz in cellSpecies[coords]: # assign carvizes to pride
                    if isinstance(carviz,Carviz):
                        mostSocialPride.addComponent(carviz)

    def fight(self, pride1:Pride, pride2:Pride) -> Pride:
        """ takes two prides, the two strongest individuals fight to death until no more individuals are present, returns the winning pride """
        p1Carvizes = sorted(pride1.getComponents(), key = lambda x : x.getEnergy())
        p2Carvizes = sorted(pride2.getComponents(), key = lambda x : x.getEnergy())
        while(len(p1Carvizes) > 0 and len(p2Carvizes) > 0):
            c1 = p1Carvizes[-1]
            c2 = p2Carvizes[-1]
            c1Energy = c1.getEnergy()
            c2Energy = c2.getEnergy()
            if c1Energy > c2Energy: # c1 wins
                self.creatureDeath(c2)
                p2Carvizes.pop()
                c1.changeEnergy(c2Energy)
                p1Carvizes.sort(key = lambda x : x.getEnergy())
            elif c1Energy < c2Energy:
                self.creatureDeath(c1)
                p1Carvizes.pop()
                c1.changeEnergy(c2Energy)
                p2Carvizes.sort(key = lambda x : x.getEnergy())
            else:
                self.creatureDeath(c1)
                self.creatureDeath(c2)
                p1Carvizes.pop()
                p2Carvizes.pop()

        if (len(p1Carvizes) == 0):
            pride1.disband()
            return pride2
        else:
            pride2.disband()
            return pride1

    def struggle(self):
        """
        If  more  than  one  Carviz  pride  reach  the  cell, they  evaluate  the  joining  in  a  single  pride.
        The evaluation is made on pride-basis, using the social attitude of their members.
        If one of the pridesdecide not to join, a fight takes place. In case of more than two prides reaching the same cell,
        the above procedure is applied iteratively to pairs of prides (i.e.,  starting from those with lessindividuals).
        The prides that decided to join can form the single pride before starting the figh

        Handles also alone carvizes considering to form a pride
        """

        # Prides
        cellSpecies = self.getCellSpeciesDict(self.getPrides())
        for cellCoords in cellSpecies:
            if len(cellSpecies[cellCoords]) >= 2:
                prideOrdered = sorted([pride for pride in cellSpecies[cellCoords]], key = lambda x:x.numComponents, reverse = True)
                pride1 = None
                pride2 = None
                while prideOrdered:
                    if not pride1:
                        pride1 = prideOrdered.pop()
                        pride2 = prideOrdered.pop()
                    else:
                        pride2 = prideOrdered.pop()
                    
                    if pride1.getGroupSociality() + pride2.getGroupSociality() >= 0.9: # join
                        if pride1.numComponents >= pride2.numComponents:
                            pride1.joinGroups(pride2)
                        else:
                            pride2.joinGroups(pride1)
                            pride1 = pride2
                    else:
                        winner = self.fight(pride1,pride2)
                        pride1 = winner

        # Alone Carvizes
        cellAloneCarvizes = self.getCellSpeciesDict(self.getAloneCarviz())
        for cellCoords in cellAloneCarvizes:
            if len(cellAloneCarvizes[cellCoords]) >= 2:
                carvizes = cellAloneCarvizes[cellCoords]
                if sum([carv.getSocialAttitude() for carv in carvizes]) >= 0.45 * len(carvizes):
                    # create a pride
                    for c in carvizes:
                        self.remove(c)
                    newPride = Pride(carvizes)
                    self.add(newPride)
                else:
                    # fight for alone carvizes
                    carvizes = sorted(carvizes, key = lambda x : x.getEnergy())
                    lastCarviz = carvizes.pop()
                    secondCarvizEnergy = carvizes[-1].getEnergy()
                    for c in carvizes:
                        self.creatureDeath(c)
                    if lastCarviz.getEnergy() <= secondCarvizEnergy:
                        self.creatureDeath(lastCarviz)
                    else:
                        lastCarviz.changeEnergy(-secondCarvizEnergy)

    def _hunt_probability(self, victim_strength, group_strength, k=2.5):
        """
        Calculates the probability of the group successfully hunting the victim.
        """
        strength_difference = group_strength - victim_strength
        probability = 1 / (1 + np.exp(-k * strength_difference))
        return probability

    def hunt(self):
        """
        hunting, it is assumed that no multiple pride and herd can coexist in the same cell
        The Hunting method adopted is 'Last Blood' with a probability of success based on the difference in strength between the group and the victim and 3 attempts
        """

        cellHunters = self.getCellSpeciesDict(self.getPrides() + self.getAloneCarviz())
        cellHerds = self.getCellSpeciesDict(self.getHerds())
        cellErbasts = self.getCellSpeciesDict(self.getAloneErbasts())

        for coords in cellHunters:
            if coords in cellHerds or coords in cellErbasts:

                # retrieve the strongest erbast and the pride
                if coords in cellHerds:
                    herd = cellHerds[coords][0]
                    strongestErbast = max(herd.getComponents(), key = lambda x : x.getEnergy())
                else:
                    strongestErbast = cellErbasts[coords][0]

                hunter = cellHunters[coords][0]

                attempts = 0

                # calculate the outcome of the hunt
                erbastEnergy = strongestErbast.getEnergy()
                if isinstance(hunter, Pride):
                    numPrideComponents = len(hunter.getComponents())
                    hunterStrength = hunter.getGroupEnergy() * numPrideComponents * hunter.getGroupSociality()
                elif isinstance(hunter, Carviz):
                    hunterStrength = hunter.getEnergy() * (2 - hunter.getSocialAttitude())

                erbastLuck = random.randint(1,3)
                huntProbability = self._hunt_probability(erbastEnergy, hunterStrength) * erbastLuck

                while attempts < 3:

                    if isinstance(hunter, Pride):

                        if random.random() < huntProbability: # death
                            self.creatureDeath(strongestErbast)

                            # energy sharing
                            individualShare = erbastEnergy // numPrideComponents
                            hunter.changeEnergy(individualShare)

                            # the hungriest carviz gets the spare energy
                            spareEnergy = erbastEnergy % numPrideComponents
                            hungriestCarviz = min(hunter.getComponents(), key = lambda x : x.getEnergy())
                            hungriestCarviz.changeEnergy(spareEnergy) 
                            break
                        else:
                            attempts += 1
                            self.changeEnergyAndHandleDeath(hunter, -5)
                    
                    elif isinstance(hunter, Carviz):
                        
                        if random.random() < huntProbability: # death
                            self.creatureDeath(strongestErbast)
                            hunter.changeEnergy(erbastEnergy)
                            break
                        else:
                            attempts += 1
                            self.changeEnergyAndHandleDeath(hunter, -5)

    def nextDay(self):
        """The days phase happens one after the other until the new day"""

        self.day += 1

        print(f"day {self.day}")

        grid = self.getGrid()
        cells = grid.reshape(-1)
        landCells = [landC for landC in cells if isinstance(landC,LandCell)]
        # 3.1 - GROWING
        for cell in landCells:
            cell.growVegetob()

        # 3.2 - MOVEMENT

        species = self.getAloneErbasts() + self.getHerds() + self.getAloneCarviz() + self.getPrides()

        stayingCreatures = []
        nextCoords = dict() # of moving creatures
        
        for c in species:
            nextCoords.update(c.moveChoice(worldGrid = grid))

        nextCoords_tmp = nextCoords.copy()

        for c in nextCoords_tmp:
            if c.getCoords() == nextCoords[c]: # staying
                stayingCreatures.append(c)
                nextCoords.pop(c)
            else: # moving
                if not self.changeEnergyAndHandleDeath(c, ENERGY_LOSS):
                    nextCoords.pop(c)
                
        self.move(nextCoords)


        # 3.3 - GRAZING
        stayingErbast = [e for e in stayingCreatures if isinstance(e, Erbast) or isinstance(e,Herd)]
        for e in stayingErbast:
            self.graze(e) #this includes cell vegetob reduction, herd and individual energy increase

        # 3.4 - STRUGGLE

        # Erbasts are automatically merged in Herds from LandCell internal updates when trying to add them

        # two important things are going to happen: Alone carvizes joining a pride and pride struggling
        # the order here matters and would promote or not change the win of the group with the higher social Attitude
        # the order will be random

        orderCarvizJoins = random.randint(0,1)

        if orderCarvizJoins == 0:
            self.joinCarvizesToPride()
            self.struggle()
        elif orderCarvizJoins == 1:
            self.struggle()
            self.joinCarvizesToPride()
        
        # 3.4 - HUNT

        self.hunt()

        # 3.5 - SPAWNING
        for c in self.creatures["Erbast"] + self.creatures["Carviz"]:
            alive = c.ageStep()
            if not alive:
                self.creatureDeath(c)

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
    def createWorld(self, typology = "fbm", threshold = 0.2) -> np.ndarray:
        """
        Initialize the world
        Vegetob density starts at around 25
        """
        
        if typology == "fbm":
            values_grid = self.__fbmNoise(NUMCELLS, threshold, seed=None, dynamic=True)
            grid = np.zeros((NUMCELLS, NUMCELLS), dtype=object)
            for i in range(NUMCELLS):
                for j in range(NUMCELLS):
                    if values_grid[i][j] > threshold:
                        grid[i][j] = LandCell((i, j), Vegetob(density=40 + random.randint(-30, 40)))
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

    def getCoords(self) -> tuple:
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
        self.prides = []
        self.numErbast = 0
        self.numCarviz = 0

    def getVegetobDensity(self):
        """Get Vegetob Density in the cell"""
        return self.vegetob.density
    
    def growVegetob(self, times:int = 1):
        """Grow the Vegetob population in the cell"""
        self.vegetob.grow(times)

    def reduceVegetob(self, amount:int = 5):
        if not isinstance(amount, int):
            raise TypeError(f"amount must be an integer, received {type(amount)}")
        """apply grazing effects on the Vegetob population in the cell"""
        self.vegetob.reduce(amount)

    def addAnimal(self, animal:'Animal'):
        """add an animal from the inhabitants list"""
        
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

        if isinstance(animal, Carviz): # pride logic handled by struggle
            self.creatures["Carviz"].append(animal)
            self.numCarviz += 1

    def removeAnimal(self, animal:'Animal'): 
        """Remove an animal from the inhabitants list"""
        if isinstance(animal, Erbast):
            if animal in self.creatures["Erbast"]:

                if self.numErbast == 0 and not self.herd:
                    raise Exception(f"{animal} is not present in the cell {self}, hence it can't be removed. The cell is empty")
                
                elif self.numErbast == 1 and not self.herd:
                    self.numErbast -= 1
                    self.creatures["Erbast"].remove(animal)

                elif self.numErbast == 2 and self.herd:
                    presentHerd = self.herd
                    presentHerd.loseComponent(animal)
                    try:
                        remainingAnimal = presentHerd.getComponents()[0]
                    except IndexError:
                        raise Exception(f"herd {presentHerd} is empty, this should not happen, numErbast: {self.numErbast}, self.herd: {self.herd}, creatures: {self.creatures['Erbast']}")
                    remainingAnimal.inSocialGroup = False
                    remainingAnimal.socialGroup = None
                    self.removeHerd()
                    self.addAnimal(remainingAnimal)

                elif self.numErbast > 2 and self.herd: 
                    self.creatures["Erbast"].remove(animal)
                    self.numErbast -= 1
                    self.herd.loseComponent(animal)

                else:
                    raise Exception(f"This should not happen, tried to remove {animal} from the cell {self}, herd: {self.herd}, numErbast: {self.numErbast}")
                
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
            else:
                if self.numErbast == 1:
                    presentAnimal = self.creatures["Erbast"][0]
                    self.removeAnimal(presentAnimal)
                    group.addComponent(presentAnimal)
                self.herd = group
                self.creatures["Erbast"].extend(group.getComponents())
                self.numErbast += group.numComponents

        elif isinstance(group, Pride): # pride logic handled by struggle
            self.prides.append(group)
            self.creatures["Carviz"].extend(group.getComponents())
            self.numCarviz += group.numComponents

    def removeHerd(self):
        """Remove the herd from the landCell"""
        if self.herd is not None:
            self.creatures["Erbast"] = [erb for erb in self.creatures["Erbast"] if erb not in self.herd.getComponents()]
            self.numErbast -= self.herd.numComponents
            self.herd = None

    def removePride(self, pride:'Pride'):
        """Remove the pride from the landCell"""
        self.creatures["Carviz"] = [car for car in self.creatures["Carviz"] if car not in pride.getComponents()]
        self.numCarviz -= pride.numComponents
        self.prides.remove(pride)

    def getErbastList(self):
        """Get a list of all Erbast inhabitants in the cell"""
        return self.creatures["Erbast"]

    def getCarvizList(self):
        """Get a list of all Carviz inhabitants in the cell"""
        return self.creatures["Carviz"]

    def getCellType(self):
        return "land"

    def getHerd(self):
        return self.herd
    
    def getPrides(self):
        return self.prides
    
    def __repr__(self):
        return f"LandCell {self.coords}"
