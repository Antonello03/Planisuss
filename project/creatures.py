from planisuss_constants import *
import numpy as np
import sys
import random
import math
import logging
from typing import TYPE_CHECKING # to avoid vscode telling me i'm not including libraries that would cause a circular import
if TYPE_CHECKING:
    from world import WorldGrid

def getDirection(myCoords:tuple ,otherCoords:tuple):
    """given to coords tuple return direction"""
    myX, myY = myCoords
    otherX, otherY = otherCoords
    if otherX < myX:
        if otherY < myY:
            return 'NW'
        elif otherY == myY:
            return 'N'
        else:
            return 'NE'
    elif otherX == myX:
        if otherY < myY:
            return 'O'
        elif otherY == myY:
            return None
        else:
            return 'E'
    else:
        if otherY < myY:
            return 'SW'
        elif otherY == myY:
            return 'S'
        else:
            return 'SE'
def getOppositeDirection(myCoords:tuple, otherCoords:tuple):
    return getDirection(otherCoords, myCoords)
def getCellInDirection(myCoords:tuple, direction:str):
    x,y = myCoords
    if direction == "N":
        return (x-1,y)
    elif direction == "NE":
        return (x-1,y+1)
    elif direction == "E":
        return (x,y+1)
    elif direction == "SE":
        return (x+1,y+1)
    elif direction == "S":
        return (x+1,y)
    elif direction == "SW":
        return (x+1,y-1)
    elif direction == "W":
        return (x,y-1)
    elif direction == "NW":
        return (x-1,y-1)
    else:
        return myCoords
    
def checkCoordsInBoundary(coords):
    if coords[0] >= 0 and coords[0] < NUMCELLS and coords[1] >= 0 and coords[1] < NUMCELLS:
        return True
    else:
        return False

class Species():
    """Class from which Erbasts, Carvizes, Herds and Prides inherit"""
    def __init__(self):
        pass

    def moveChoice(self, worldGrid:'WorldGrid') -> dict['Species', tuple[int, int]]:
        pass

    def getNeighborhood(self, worldGrid:'WorldGrid', d = None):
        """
        This method return the neighborhood of the animal or socialGroup considered, this approach requires storing the worldGrid
        
        The worldGrid is passed as an argument to keep the Animal/ SocialGroup class loosely coupled 
        and focused solely on animal-specific behavior. This approach enhances flexibility, 
        maintainability, and testability by avoiding direct dependencies between Animal and 
        a specific WorldGrid instance.
        """
        x, y = self.coords[0], self.coords[1]
        d = d if d is not None else self.neighborhoodDistance
        x_min = max(0, x - d)
        x_max = min(NUMCELLS_R, x + d + 1)
        y_min = max(0, y - d)
        y_max = min(NUMCELLS_C, y + d + 1)
        cands = worldGrid[x_min:x_max, y_min:y_max].reshape(-1)

        logging.debug(f"{self}, in position {self.getCoords()}, with neighborhood distance {d} was looking for its neighborhood, i returned {cands}")

        # print(f"{self} was looking for its neighborhood, i returned {cands}, with neighborhood {d}")
        # cands = np.delete(cands,len(cands)//2)
        return cands

    def changeEnergy(self, amount:int):
        pass

    def getCell(self, grid:'WorldGrid'):
        return grid[self.getCoords()]

    def getCoords(self):
        return self.coords

class Animal(Species):

    def __init__(self, coordinates: tuple, energy:int = MAX_ENERGY, lifetime:int = MAX_LIFE, age:int = 0, SocialAttitude:float = 0.5, neighborhoodDistance = NEIGHBORHOOD, name:str = None):
        super().__init__()
        self.coords = coordinates
        self.energy = energy
        self.lifetime = lifetime
        self.age = age
        self.socialAttitude = SocialAttitude
        self.socialGroup = None
        self.inSocialGroup = False
        self.alive = True
        self.neighborhoodDistance = neighborhoodDistance
        self.preferredDirection = None
        self.preferredDirectionIntensity = 1 # number from 0 to 1
        self.name = name

    def getSocialAttitude(self):
        return self.socialAttitude
    
    def getSocialGroup(self):
        return self.socialGroup

    def getEnergy(self):
        return self.energy

    def changeEnergy(self, amount:int):
        """Change the energy of the animal by the specified amount, returns if the animal is alive"""
        if not isinstance(amount, int):
            raise ValueError("amount must be an integer")
        if 0 <= self.energy + amount <= MAX_ENERGY:
            self.energy += amount
        elif self.energy + amount < 0:
            self.energy = 0
            self.alive = False
            logging.info(f"{self} died of starvation")
        else:
            self.energy = MAX_ENERGY
        return {self:self.alive}

    def ageStep(self, days:int = 1):
        """Increase the age of the animal by the specified number of days. returns if the animal is alive (True) or dead (False)"""
        if self.alive:
            if not isinstance(days, int):
                raise ValueError("days must be an integer")
            if self.age + days <= self.lifetime:
                self.age += days
            else: 
                self.age = self.lifetime
                self.alive = False
                logging.info(f"{self} died of old age")
            if self.age % 10 == 0:
                self.energy -= AGING
                if self.energy <= 0:
                    self.energy = 0
                    self.alive = False
                    logging.info(f"{self} died of starvation due to aging")
        else:
            raise RuntimeError(f"Cannot age a dead animal: {self}, age: {self.age}, lifetime: {self.lifetime}")
        
        return self.alive

    def die(self):
        if isinstance(self, Carviz) and self.inSocialGroup:
            socG = self.socialGroup
            socG.loseComponent(self)
        self.alive = False
        self.energy = 0
        return self

    def moveChoice(self, worldGrid: 'WorldGrid') -> dict['Species', tuple[int, int]]:
        """handles group"""
        moveValues = self.rankMoves(worldGrid)
        return {self: max(moveValues, key=moveValues.get)}

class Vegetob():

    """
    Our cute plants, growing each day... unable to move...
    """
    
    def __init__(self, density = 0):
        super().__init__()
        self.density = density

    def grow(self, times:int = 1):
        """Grow the Vegetob"""
        if not isinstance(times, int):
            raise ValueError("times must be an integer")
        for _ in range(times):
            if self.density + GROWING <= MAX_GROWTH:
                self.density += GROWING
            else:
                self.density = MAX_GROWTH

    def reduce(self, amount:int = 5):
        """Apply Grazing Effect"""
        if not isinstance(amount, int):
            raise ValueError("amount must be an integer")
        if self.density - amount >= 0:
            self.density -= amount
        else:
            self.density = 0

    def __repr__(self):
        return "Vegetob"

class Erbast(Animal):
    """
    Herbivore dude eat grass and die
    Erbasts are generally friendly, their socialAttitude score goes from low - 0 to high - 1
    """
    ID = 1

    CARVIZ_DANGER = 1.5
    VEG_NEED = 0.01

    ENERGY_WEIGHT1 = 2 # scales how much energy matters overall
    ENERGY_WEIGHT2 = 0.1 # regulates how much the percentage of energy matters

    ESCAPE_DECAY = 0.8 #for how much time an erbast wants to go in the opposite direction of the last saw carviz
    ESCAPE_THRESHOLD = 0.3 #Under which value erbast no longer run away
    NOT_EATING_SA_REDUCTION = 0.05

    def __init__(self, coordinates: tuple, energy:int = MAX_ENERGY_E, lifetime:int = MAX_LIFE_E, age:int = 0, SocialAttitude:float = 0.5, name:str = None):
        super().__init__(coordinates, energy, lifetime, age, SocialAttitude, name = name)
        self.id = Erbast.ID
        Erbast.ID += 1

    def rankMoves(self, worldGrid:'WorldGrid'):
        """
        This method calculates the desirability scores for each cell in the given neighborhood and returns a dict of {cellcoords: desValue}.
        
        rankMoves updates internal parameters, hence if used more times with the same configuration results may differ
        """

        neighborhood = self.getNeighborhood(worldGrid, self.neighborhoodDistance)
        LandCell = getattr(sys.modules['world'], 'LandCell')
        neighborhood = [cell for cell in neighborhood if isinstance(cell, LandCell)]
        desirabilityScores = {cell:0 for cell in neighborhood}
        presentCell = self.getCell(worldGrid) # presentCell should be in neighborhood
        stayingNeed = (15 * math.exp(-Erbast.ENERGY_WEIGHT2 * self.getEnergy()) - Erbast.ENERGY_WEIGHT1) * (presentCell.getVegetobDensity()/MAX_GROWTH - 0.5)

        for cell in desirabilityScores:

            carvizDangerValue = cell.numCarviz * Erbast.CARVIZ_DANGER
            desirabilityScores[cell] -= carvizDangerValue

            # also neighbouring cells, if in range, should become more dangerous, but a bit less
            if(cell.numCarviz > 0):
                x,y = cell.getCoords()

                self.preferredDirection = getOppositeDirection(presentCell.getCoords(), (x,y)) #store last escape direction
                self.preferredDirectionIntensity = 1 # raise intensity

                nearbyCords = [(x-1, y-1),(x, y-1),(x+1, y-1),(x-1, y+1),(x, y+1),(x+1, y+1),(x-1, y),(x+1, y)]
                nearbyCells = [worldGrid[coords] for coords in nearbyCords if checkCoordsInBoundary(coords)]
                CellsInRange = [cell for cell in nearbyCells if cell in neighborhood]
                for cell in CellsInRange:
                    # print(f"cell {cell.getCoords()} is dangerous, it's desirability is now: {desirabilityScores[cell]}")
                    desirabilityScores[cell] -= carvizDangerValue * 0.6
                    # print(f"nerfed to {desirabilityScores[cell]} ")

            if presentCell != cell:
                desirabilityScores[cell] -= stayingNeed
                if presentCell.numErbast < cell.numErbast: # this avoid herds or individuals in swapping position indefinitely, instead the smaller group will join the bigger one, aslo self counting is avoided
                    desirabilityScores[cell] += cell.numErbast * self.socialAttitude
                elif presentCell.numErbast == cell.numErbast: # if we are the same number we can join or stay still by random choice
                    if random.random() > 0.5:
                        desirabilityScores[cell] += cell.numErbast * self.socialAttitude
                    else:
                        desirabilityScores[presentCell] += cell.numErbast * self.socialAttitude
                elif cell.numErbast > 0: #if they are not more than us, we stil want to join so we stay still
                    desirabilityScores[presentCell] += cell.numErbast * self.socialAttitude

            desirabilityScores[cell] += cell.getVegetobDensity() * Erbast.VEG_NEED

        # Staying likability evaluation
        desirabilityScores[presentCell] += stayingNeed
        
        # Running away from carviz
        escapeCellCoords = getCellInDirection(presentCell.getCoords(), self.preferredDirection)
        if checkCoordsInBoundary(escapeCellCoords):
            escapeCell = worldGrid[escapeCellCoords]
            if escapeCell in neighborhood and escapeCell != presentCell and self.preferredDirectionIntensity > Erbast.ESCAPE_THRESHOLD:
                # print(f"Oh no I'm {self}, I'm in {self.getCoords()} and there's a Carviz nearby, better go in {escapeCell.getCoords()}")
                desirabilityScores[escapeCell] += self.preferredDirectionIntensity
                self.preferredDirectionIntensity *= Erbast.ESCAPE_DECAY

        for cell in desirabilityScores:
            desirabilityScores[cell] = round(desirabilityScores[cell], 2)

        returnDict = {cell.getCoords():desirabilityScores[cell] for cell in desirabilityScores}
        return returnDict

    def graze(self, availableVegetob:int) -> int: # Vegetob reduction should be handled by environment becaus of herds dynamics
        """returns grazed amount"""
        if self.energy + availableVegetob <= MAX_ENERGY_E:
            self.energy += availableVegetob
            eatenVeg = availableVegetob
        else:
            self.energy = MAX_ENERGY_E
            eatenVeg = MAX_ENERGY_E - self.energy
        return eatenVeg
        
    def __repr__(self):
        return f"Erbast {self.id}"

class Carviz(Animal):
    """
    Angry boy very hungry

    Carvizes aren't as friendly as Erbasts, their social attitude score goes from 0 offensive to 1 friendly
    """
    ID = 1

    VEG_NEED = 0.005 # carvist do not need vegetob, but it makes sense for them to look for erbast in food rich zones #TODO but maybe it is more reasonable to look where food has been eaten?
    ERBAST_NEED = 1.2
    
    ENERGY_WEIGHT = 0.1 # scales how much energy matters overall
    ENERGY_WEIGHT2 = 0.8 # lower value -> more likely to stay even at high energy levels
    ENERGY_EXPONENT = 0.65 # regulates how much the percentage of energy matters

    def __init__(self, coordinates: tuple, energy:int = MAX_ENERGY_C, lifetime:int = MAX_LIFE_C, age:int = 0, SocialAttitude:float = 0.5, neighborhoodDistance = NEIGHBORHOOD_C, name:str = None):
        super().__init__(coordinates, energy, lifetime, age, SocialAttitude, neighborhoodDistance, name = name)
        self.id = Carviz.ID
        Carviz.ID += 1

    def rankMoves(self, worldGrid: 'WorldGrid'):
        """Ranks the moves in the neighborhood based on desirability scores."""
        neighborhood = self.getNeighborhood(worldGrid, d = self.neighborhoodDistance)
        reachableCells = self.getNeighborhood(worldGrid, d = 1)
        LandCell = getattr(sys.modules['world'], 'LandCell')
        neighborhood = [cell for cell in neighborhood if isinstance(cell, LandCell)]
        reachableCells = [el for el in reachableCells if isinstance(el, LandCell)]
        desirabilityScores = {cell:0 for cell in neighborhood}
        presentCell = self.getCell(worldGrid) # presentCell should be in neighborhood

        # Carviz are very hungry and they want to eat Erbasts
        for cell in desirabilityScores:
            desirabilityScores[cell] += cell.numErbast * Carviz.ERBAST_NEED

            # also neighbouring cells, if in range, should become more attractive, but a bit less
            if(cell.numErbast > 0):
                x,y = cell.getCoords()
                nearbyCords = [(x-1, y-1),(x, y-1),(x+1, y-1),(x-1, y+1),(x, y+1),(x+1, y+1),(x-1, y),(x+1, y)]
                nearbyCells = [worldGrid[coords] for coords in nearbyCords if checkCoordsInBoundary(coords)]
                CellsInRange = [cell for cell in nearbyCells if cell in reachableCells]
                for cell in CellsInRange:
                    desirabilityScores[cell] += cell.numErbast * 0.6

            desirabilityScores[cell] += cell.getVegetobDensity() * Carviz.VEG_NEED
            
            #do we want to meet other carvizes?
            if presentCell != cell:
                if presentCell.numCarviz < cell.numCarviz:
                    desirabilityScores[cell] += cell.numCarviz * (self.socialAttitude - 0.5) # A carviz might want to stay alone
                elif presentCell.numCarviz == cell.numCarviz: # if we are the same number we can join or stay still by random choice
                    if random.random() > 0.5:
                        desirabilityScores[cell] += cell.numCarviz * self.socialAttitude
                    else:
                        desirabilityScores[presentCell] += cell.numCarviz * self.socialAttitude
                elif cell.numCarviz > 0:
                    desirabilityScores[presentCell] += cell.numCarviz * (self.socialAttitude - 0.5)

        # Staying likability evaluation - carviz are very unlikely to stay still, they're constantly looking for Erbasts
        desirabilityScores[presentCell] -= round(((100 - self.energy)**Carviz.ENERGY_EXPONENT * Carviz.ENERGY_WEIGHT),2) #when the energy is low a prey must be found

        for cell in desirabilityScores:
            desirabilityScores[cell] = round(desirabilityScores[cell], 2)

        returnDict = {cell.getCoords():desirabilityScores[cell] for cell in desirabilityScores if cell in reachableCells}
        return returnDict

    def __repr__(self):
        return f"Carviz {self.id}"

class SocialGroup(Species): # TODO what particular information may be stored by a socialGroup?, lastoords might be an array of fixed length
    """
    Holds knowledge about the environment
    """   

    GOING_BACK_PENALTY = 0.3

    def __init__(self, components : list[Animal], neighborhoodDistance = NEIGHBORHOOD_SOCIAL, memory = MEMORY_SOCIAL):

        super().__init__()
        self.coords = (-1,-1)
        self.lastCoords = []
        if (len(components) > 0):
            self.coords = components[0].getCoords()
            self.lastCoords.append(self.coords)
            for animal in components:
                if not isinstance(animal, Animal):
                    raise Exception(f"All Individuals should be Animals, received instead {animal}")
                if animal.getCoords() != self.coords:
                    raise Exception(f"All Animals should inhabit the same cell, individual {animal} is in {animal.getCoords()}, it should be in {self.coords}. Herd is {self}, components are {components}")

        self.components = components
        
        for el in self.components:
            el.inSocialGroup = True
            el.socialGroup = self

        self.numComponents = len(components)
        self.neighborhoodDistance = neighborhoodDistance
        self.memory = memory

    def updateCoords(self, newCoords:tuple[int,int]):
        """Should always be used to update Coords"""
        self.lastCoords.append(self.coords)
        self.coords = newCoords
    
    def getGroupSociality(self):
        totSocial = 0
        for component in self.components:
            totSocial += component.socialAttitude
        return round(totSocial / self.numComponents , 2)
    
    def getGroupEnergy(self):
        totalEnergy = 0
        for component in self.components:
            totalEnergy += component.energy
        return round(totalEnergy / self.numComponents , 2)

    def changeEnergy(self, amount:int):
        """Change the energy of each individual in the group by the specified amount, returns dictionary of alive creatures"""
        if not isinstance(amount, int):
            raise ValueError("amount must be an integer")
        aliveDict = dict()
        for component in self.components:
            component.changeEnergy(amount)
            aliveDict[component] = component.alive
        return aliveDict

    def getComponents(self):
        return self.components
    
    def addComponent(self, animal:Animal):
        if not isinstance(animal, Animal):
            raise ValueError("animal must be an instance of Animal")
        
        self.components.append(animal)
        animal.inSocialGroup = True
        animal.socialGroup = self
        self.numComponents += 1

    def joinGroups(self, other:'SocialGroup'):
        self.components.extend(other.components)
        self.numComponents = len(self.components)
        componentesToRemove = other.components.copy()
        for el in componentesToRemove:
            other.loseComponent(el)
            el.socialGroup = self
            el.inSocialGroup = True
        other.numComponents = 0
        # TODO -join knowledge        
    
    def loseComponent(self, animal:Animal):
        if not isinstance(animal, Animal):
            raise ValueError("animal must be an instance of Animal")
        
        if len(self.components) == 2:
            self.components.remove(animal)
            animal.inSocialGroup = False
            animal.socialGroup = None
            lastAnimal = self.components[0]
            lastAnimal.inSocialGroup = False
            lastAnimal.socialGroup = None
            self.components.remove(lastAnimal)
            self.numComponents == 0
            return  {
                "result": "Group Disbanded",
                "individuals":[animal,lastAnimal]
                }
        elif len(self.components) == 1:
            self.components.remove(animal)
            animal.inSocialGroup = False
            animal.socialGroup = None
            self.numComponents -= 1
            return {
                "result": "Group Disbanded",
                "lost individual": animal
            }
        elif len(self.components) == 0:
            return {
                "result": "Group Already Disbanded",
                "individuals":[]
                }
        else:
            self.components.remove(animal)
            animal.inSocialGroup = False
            animal.socialGroup = None
            self.numComponents -= 1
            return {
                "result": "All Good",
                "lost individual": animal
            }

    def disband(self):
        """Remove all components from group and set numComponents from 0, returns the empty group"""
        for el in self.components:
            el.socialGroup = None
            el.inSocialGroup = False
        self.numComponents = 0
        return self

    def moveChoice(self, worldGrid: 'WorldGrid') -> dict['Species', tuple[int, int]]:
        """
        In this method the group decision is assessed and eventual leaving components are identified with their preferred direction,
        if applyConsequences is True, leaving individuals will be removed from the herd
        """


        moveValues = self.rankMoves(worldGrid)
        groupdecidedCoords = max(moveValues, key=moveValues.get)

        logging.info(f"Group {self}, components: {self.getComponents()} want to go in {groupdecidedCoords}")

        leavingIndividualsAndDirection = dict()
        for c in self.getComponents():
            individualValues = c.rankMoves(worldGrid)

            if groupdecidedCoords not in individualValues.keys():
                logging.error(f"Individual {c} in {c.getCoords()} neighborhood is {individualValues.keys()}")

            if individualValues[groupdecidedCoords] < -c.socialAttitude: #if individual preference is lower than the negative social attitude for the group choice
                individualDecidedCoords = max(individualValues, key=individualValues.get)
                if groupdecidedCoords != individualDecidedCoords: #and the individual choice is different from the group choice
                    leavingIndividualsAndDirection[c] = individualDecidedCoords # get individual preferred movement
                    logging.info(f"{c} in {c.getCoords()}, differently from the group, wants to go at: {max(individualValues, key=individualValues.get)}")
                    if len(leavingIndividualsAndDirection) == self.numComponents - 1:
                        logging.info(f"The group {self} disbanded, the individuals {self.getComponents()} are now free to go")
                        components = self.getComponents()
                        lastAnimal = [x for x in components if x not in leavingIndividualsAndDirection.keys()][0]
                        lAValues = lastAnimal.rankMoves(worldGrid)
                        leavingIndividualsAndDirection[lastAnimal] = max(lAValues, key=lAValues.get)
                        return leavingIndividualsAndDirection
        
        choices = {**leavingIndividualsAndDirection, self:groupdecidedCoords}
        return choices

    def __repr__(self):
        return f"SocialGroup, components:{self.components}"
    
class Herd(SocialGroup): # TODO - Add Herd Escape rankMoves logic

    """
    Joining a Herd has several advantages for an Erbast

     - Knowledge about past visited cells
     - Knowledge about predators
     - In a Herd you have multiple eyes hence you'll be able to identify dangers at a longer distance +1 neighborhood Distance
    """

    ID = 1

    def __init__(self, components: list[Erbast]):
        super().__init__(components, neighborhoodDistance = NEIGHBORHOOD_HERD)
        self.id = Herd.ID
        Herd.ID += 1
        self.preferredDirection = None
        self.preferredDirectionIntensity = 1 # number from 0 to 1

        logging.info(f"HERD CREATION -> Herd {self.id} with components: {self.components}, current coords: {self.coords}, last coords: {self.lastCoords}, neighborhood distance: {self.neighborhoodDistance}, memory: {self.memory}")


    def rankMoves(self, worldGrid:'WorldGrid'):
        """
        Method used by a SocialGroup to decide the next move.
        Differently from Individual method of choice and Herd can take into account more factors like
        - dangers at a longer distance
        - TODO 
        """
        # First of all the Herd makes a decision based on its knowledge

        neighborhood = self.getNeighborhood(worldGrid, d = self.neighborhoodDistance)
        reachableCells = self.getNeighborhood(worldGrid, d = 1)
        LandCell = getattr(sys.modules['world'], 'LandCell')
        neighborhood = [el for el in neighborhood if isinstance(el, LandCell)]
        reachableCells = [el for el in reachableCells if isinstance(el, LandCell)]
        # print(f"neighborhood Cells: {[cell.getCoords() for cell in neighborhood]}\nreachableCells: {[cell.getCoords() for cell in reachableCells]}")
        desirabilityScores = {cell:0 for cell in neighborhood}
        groupSociality = self.getGroupSociality()
        groupEnergy = self.getGroupEnergy()
        presentCell = self.getCell(worldGrid) # presentCell should be in neighborhood

        for cell in desirabilityScores:

            carvizDangerValue = cell.numCarviz * Erbast.CARVIZ_DANGER
            desirabilityScores[cell] -= carvizDangerValue

            # also neighbouring cells, if in range, should become more dangerous, but a bit less
            # herd has a better sense of danger and try to stay as far as possible from carvizes
            if(cell.numCarviz > 0):
                x,y = cell.getCoords()

                self.preferredDirection = getOppositeDirection(presentCell.getCoords(), (x,y)) #store last escape direction
                self.preferredDirectionIntensity = 1 # raise intensity

                nearbyCords = [(x-1, y-1),(x, y-1),(x+1, y-1),(x-1, y+1),(x, y+1),(x+1, y+1),(x-1, y),(x+1, y)]
                nearbyCords_2 = [(x-2, y-2),(x-1, y-2),(x, y-2),(x+1, y-2),(x+2, y-2),
                                 (x-2, y+2),(x-1, y+2),(x, y+2),(x+1, y+2),(x+2, y+2),
                                 (x-2, y-1),(x+2, y-1),(x-2, y),(x+2, y),(x-2, y+1),(x+2, y+1)]

                nearbyCells = [worldGrid[coords] for coords in nearbyCords if checkCoordsInBoundary(coords)]
                nearbyCells_2 = [worldGrid[coords] for coords in nearbyCords_2 if checkCoordsInBoundary(coords)]

                CellsInRange = [cell for cell in nearbyCells if cell in reachableCells]
                CellsInRange_2 = [cell for cell in nearbyCells_2 if cell in reachableCells]

                for cell in CellsInRange:
                    # print(f"cell {cell.getCoords()} is dangerous, it's desirability is now: {desirabilityScores[cell]}")
                    desirabilityScores[cell] -= carvizDangerValue * 0.6
                    # print(f"nerfed to {desirabilityScores[cell]} ")
                for cell in CellsInRange_2:
                    desirabilityScores[cell] -= carvizDangerValue * 0.4

            if presentCell != cell and presentCell.numErbast < cell.numErbast:
                desirabilityScores[cell] += cell.numErbast * groupSociality

            desirabilityScores[cell] += cell.getVegetobDensity() * Erbast.VEG_NEED

            if cell in {worldGrid[coords] for coords in self.lastCoords[max(-len(self.lastCoords),-self.memory):]}: #avoid going back
                desirabilityScores[cell] -= SocialGroup.GOING_BACK_PENALTY

        # Staying likability evaluation
        desirabilityScores = {cell:desirabilityScores[cell] for cell in desirabilityScores if cell in reachableCells} # remove far away cells
        desirabilityScores[presentCell] +=  (15 * math.exp(-Erbast.ENERGY_WEIGHT2 * groupEnergy) - Erbast.ENERGY_WEIGHT1) * (presentCell.getVegetobDensity()/MAX_GROWTH - 0.5)
        
        #Runnin away from Carviz
        escapeCellCoords = getCellInDirection(presentCell.getCoords(), self.preferredDirection)
        if checkCoordsInBoundary(escapeCellCoords):
            escapeCell = worldGrid[escapeCellCoords]
            if escapeCell in neighborhood and escapeCell != presentCell and self.preferredDirectionIntensity > Erbast.ESCAPE_THRESHOLD:
                # print(f"Oh no I'm {self}, I'm in {self.getCoords()} and there's a Carviz nearby, better go in {escapeCell.getCoords()}")
                desirabilityScores[escapeCell] += self.preferredDirectionIntensity
                self.preferredDirectionIntensity *= Erbast.ESCAPE_DECAY

        for cell in desirabilityScores:
            desirabilityScores[cell] = round(desirabilityScores[cell], 2)
        returnDict = {cell.getCoords():desirabilityScores[cell] for cell in desirabilityScores}
        return returnDict

    def _getVegetobDistribution(self, energies:list[int], availableVegetob: int) -> list[int]:
        """
        internal method to asses which Erbasts are going to eat and how much, vegetob is iteratively assigned to the lowest energy erbasts untile exhaustion
        returns vegetob assignments.
        The method assumes energies are in increasing order.
        
        Example: energies: [12, 12, 20], available Vegetob: 18
        the algorithm progressively assign the available Vegetob to the i hungriest erbasts.
        - i = 1 -> [12, 12, 20] assignedV: [0, 0, 0] (no assignement since 12 - 12 = 0)
        - i = 2 -> [21, 21, 20] assignedV: [9, 9, 0] (first energies of 1 and 2 are raised to 20 because 20 - 12 = 8, then the remaining 2 energy is distribuited)
        """
        assignedV = [0 for i in range(len(energies))]
        i = 1 #index of next highest v
        while availableVegetob > 0 and i <= len(energies):
            if i < len(energies): #standard case
                v = energies[i] - energies[i-1] # check how much to balance
            else: # all erbasts have the same energy
                v = availableVegetob
            
            #check if we have enough vegetob
            if v * i < availableVegetob:
                for j in range(i):
                    assignedV[j] += v
                availableVegetob -= v * i #update available Vegetob
            else:
                splittedV = availableVegetob // i #assign splitted remaining vegetob
                for j in range(i):
                    assignedV[j] += splittedV
                availableVegetob -= splittedV * i
                if availableVegetob > 0:
                    for j in range(availableVegetob): #assign eventual surplus
                        assignedV[j] += 1
                    availableVegetob = 0
            i += 1
        assignedV = [(lambda x: MAX_ENERGY_E - y if x + y > MAX_ENERGY_E else x)(x) for x,y in zip(assignedV, energies)] # energy should be below maxEnergy
        return assignedV

    def graze(self, availableVegetob:int) -> int:
        """returns grazed amount, updates herds components energy. Vegetob reduction should be handled by environment"""
        # for each erbast I need to understand if it has eaten or not and how much he needs to eat
        energies = {erb : erb.getEnergy() for erb in self.getComponents()}
        energies = dict(sorted(energies.items(), key=lambda item: item[1])) #sort by values
        energiesList = list(energies.values())
        assignedVegetobs = self._getVegetobDistribution(energiesList, availableVegetob)
        for erb, veg in zip(energies, assignedVegetobs):
            if veg > 0:
                erb.graze(veg)
            else: #if not eating reduce socialAttitude
                erb.socialAttitude = max(0, erb.socialAttitude - Erbast.NOT_EATING_SA_REDUCTION)
        return sum(assignedVegetobs)

    def __repr__(self):
        return f"Herd {self.id}, components:{self.components}"

class Pride(SocialGroup):

    ID = 1

    def __init__(self, components: list[Carviz]):
        super().__init__(components, neighborhoodDistance = NEIGHBORHOOD_PRIDE)
        self.id = Carviz.ID
        Carviz.ID += 1

    def rankMoves(self, worldGrid:'WorldGrid'): #done, ig

        neighborhood = self.getNeighborhood(worldGrid, d = self.neighborhoodDistance)
        reachableCells = self.getNeighborhood(worldGrid, d = 1)
        LandCell = getattr(sys.modules['world'], 'LandCell')
        neighborhood = [el for el in neighborhood if isinstance(el, LandCell)]
        reachableCells = [el for el in reachableCells if isinstance(el, LandCell)]
        # print(f"neighborhood Cells: {[cell.getCoords() for cell in neighborhood]}\nreachableCells: {[cell.getCoords() for cell in reachableCells]}")
        desirabilityScores = {cell:0 for cell in neighborhood}
        groupSociality = self.getGroupSociality()
        groupEnergy = self.getGroupEnergy()
        presentCell = self.getCell(worldGrid) # presentCell should be in neighborhood

        for cell in desirabilityScores:

            desirabilityScores[cell] += cell.numErbast * Carviz.ERBAST_NEED

            # also neighbouring cells, if in range, should become more attractive, but a bit less
            if(cell.numErbast > 0):
                x,y = cell.getCoords()
                # TODO - should use a function...
                nearbyCords = [(x-1, y-1),(x, y-1),(x+1, y-1),(x-1, y+1),(x, y+1),(x+1, y+1),(x-1, y),(x+1, y)]
                nearbyCords_2 = [(x-2, y-2),(x-1, y-2),(x, y-2),(x+1, y-2),(x+2, y-2),
                                 (x-2, y+2),(x-1, y+2),(x, y+2),(x+1, y+2),(x+2, y+2),
                                 (x-2, y-1),(x+2, y-1),(x-2, y),(x+2, y),(x-2, y+1),(x+2, y+1)]
                nearbyCoords_3 = [(x-3, y-3),(x-2, y-3),(x-1, y-3),(x, y-3),(x+1, y-3),(x+2, y-3),(x+3, y-3),
                                    (x-3, y+3),(x-2, y+3),(x-1, y+3),(x, y+3),(x+1, y+3),(x+2, y+3),(x+3, y+3),
                                    (x-3, y-2),(x+3, y-2),(x-3, y-1),(x+3, y-1),(x-3, y),(x+3, y),(x-3, y+1),(x+3, y+1),(x-3, y+2),(x+3, y+2)]
                nearbyCells = [worldGrid[coords] for coords in nearbyCords if checkCoordsInBoundary(coords)]
                nearbyCells_2 = [worldGrid[coords] for coords in nearbyCords_2 if checkCoordsInBoundary(coords)]
                nearbyCells_3 = [worldGrid[coords] for coords in nearbyCoords_3 if checkCoordsInBoundary(coords)]

                CellsInRange = [cell for cell in nearbyCells if cell in reachableCells]
                CellsInRange_2 = [cell for cell in nearbyCells_2 if cell in reachableCells]
                CellsInRange_3 = [cell for cell in nearbyCells_3 if cell in reachableCells]

                for cell in CellsInRange:
                    desirabilityScores[cell] += cell.numErbast * 0.6

                for cell in CellsInRange_2:
                    desirabilityScores[cell] += cell.numErbast * 0.4

                for cell in CellsInRange_3:
                    desirabilityScores[cell] += cell.numErbast * 0.3

            # Vegetob is not a priority for Carvizes, but it makes sense for them to look for Erbasts in food rich zones
            desirabilityScores[cell] += cell.getVegetobDensity() * Carviz.VEG_NEED
            desirabilityScores[cell] = round(desirabilityScores[cell], 2)

            #do we want to meet other carvizes?
            if presentCell != cell:
                if presentCell.numCarviz < cell.numCarviz:
                    desirabilityScores[cell] += cell.numCarviz * (self.getGroupSociality() - 0.5) # A Pride might want to stay alone
                elif cell.numCarviz > 0:
                    desirabilityScores[presentCell] += cell.numCarviz * (self.getGroupSociality() - 0.5)

        desirabilityScores = {cell:desirabilityScores[cell] for cell in desirabilityScores if cell in reachableCells} # remove far away cells
        
        # Staying likability evaluation - carviz are very unlikely to stay still, they're constantly looking for Erbasts
        desirabilityScores[presentCell] -= ((100 - self.getGroupEnergy())**Carviz.ENERGY_EXPONENT * Carviz.ENERGY_WEIGHT) #when the energy is low a prey must be found
        desirabilityScores[presentCell] = round(desirabilityScores[presentCell], 2)

        returnDict = {cell.getCoords():desirabilityScores[cell] for cell in desirabilityScores}
        return returnDict

    def __repr__(self):
        return f"Pride {self.id}, components: {self.components}"
    
class DeadCreature():

    def __init__(self, animal:Animal, day:int):
        self.coords = animal.getCoords()
        self.deadAnimal = animal
        self.deathDay = day
        self.id = animal.id
        self.old_species = animal.__class__.__name__
    
    def getDeathDay(self):
        return self.deathDay
    
    def getCoords(self) -> tuple[int]:
        return self.coords
    
    def __repr__(self):
        return f"Dead {self.deadAnimal} (from day {self.deathDay})"