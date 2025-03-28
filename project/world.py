from collections import defaultdict
import random
from creatures import Vegetob, Erbast, Carviz, Animal, SocialGroup, Herd, Pride, Species, DeadCreature
from planisuss_constants import *
from typing import Union
import numpy as np
import noise
import json
import logging
import pprint

ON = 255
OFF = 0

class Environment:
    """
    The Environment class is the core of Planisuss world.
    Each living being and the worldGrid itself is contained here and the inizialization
    and update logic of the world is managed by the following functions
    """
    def __init__(self, threshold=0.2, seed=None, octaves=8, persistence=0.4, lacunarity=1.8, scale=40.0, dynamic=False):
        self.world = WorldGrid(threshold=threshold, seed=seed, octaves=octaves, persistence=persistence, lacunarity=lacunarity, scale=scale, dynamic=dynamic)
        self.creatures = {
            "Erbast" : [],
            "Carviz" : []
        }
        self.deadCreatures = []
        self.totErbast = 0
        self.totCarviz = 0
        self.day = -1

        self.statistics = {
            "Number of Erbasts" : [],
            "Number of Carvizes" : [],
            "Number of Herds" : [],
            "Number of Prides" : [],
            "Average Herd Size" : [],
            "Average Pride Size" : [],
            "Average Erbast Energy" : [],
            "Average Carviz Energy" : [],
            "Number of Dead Creatures" : [],
            "Successfull Hunts" : [],
            "Number of Hunts" : [],
            "Average Vegetob Density" : [],
            "Average Erbast Social Attitude" : [],
            "Average Carviz Social Attitude" : [],
        }

    def computeStatistics(self, totHunts = 0, succesfulHunts = 0):
        """
        Compute statistics for the current day
        """
        self.statistics["Number of Erbasts"].append(self.totErbast)
        self.statistics["Number of Carvizes"].append(self.totCarviz)
        self.statistics["Number of Herds"].append(len(self.getHerds()))
        self.statistics["Number of Prides"].append(len(self.getPrides()))
        self.statistics["Average Herd Size"].append(sum([len(herd.getComponents()) for herd in self.getHerds()]) / len(self.getHerds()) if len(self.getHerds()) > 0 else 0)
        self.statistics["Average Pride Size"].append(sum([len(pride.getComponents()) for pride in self.getPrides()]) / len(self.getPrides()) if len(self.getPrides()) > 0 else 0)
        self.statistics["Average Erbast Energy"].append(sum([erb.getEnergy() for erb in self.creatures["Erbast"]]) / len(self.creatures["Erbast"]) if len(self.creatures["Erbast"]) > 0 else 0)
        self.statistics["Average Carviz Energy"].append(sum([carv.getEnergy() for carv in self.creatures["Carviz"]]) / len(self.creatures["Carviz"]) if len(self.creatures["Carviz"]) > 0 else 0)
        self.statistics["Number of Dead Creatures"].append(len(self.deadCreatures))
        self.statistics["Number of Hunts"].append(totHunts)
        self.statistics["Successfull Hunts"].append(succesfulHunts)
        self.statistics["Average Vegetob Density"].append(sum([cell.getVegetobDensity() for cell in self.world.grid.reshape(-1) if isinstance(cell, LandCell)]) / len([cell for cell in self.world.grid.reshape(-1) if isinstance(cell, LandCell)]))
        self.statistics["Average Erbast Social Attitude"].append(sum([erb.getSocialAttitude() for erb in self.creatures["Erbast"]]) / len(self.creatures["Erbast"]) if len(self.creatures["Erbast"]) > 0 else 0)
        self.statistics["Average Carviz Social Attitude"].append(sum([carv.getSocialAttitude() for carv in self.creatures["Carviz"]]) / len(self.creatures["Carviz"]) if len(self.creatures["Carviz"]) > 0 else 0)

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

    def isLand(self, x, y):
        return isinstance(self.getGrid()[x][y], LandCell)

    def addAnimal(self, animal:Animal):
        """
        My approach where each landCell know its inhabitants,
        each creature know its coordinates and the whole environment knows everything
        need a bit more care when managing inhabitants
        """
        if not isinstance(animal, Animal):
            raise TypeError(f"{animal} is not an Animal")
        
        x,y = animal.getCoords()

        if not self.isLand(x,y):
            raise Exception(f"Cannot add animal: {animal}, at coords {animal.getCoords()} is not in a LandCell")

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

            return aliveDict   

        elif isinstance(species, Animal):
            alive = species.changeEnergy(energy)[species]
            if not alive:
                self.creatureDeath(species)
            return {species:alive}

        else:
            raise TypeError(f"{species} is not an Animal or a SocialGroup")

    def creatureDeath(self, animal:Animal):
        """Handles the death of a creature"""
        animal.die()
        self.addDeadCreature(DeadCreature(animal, self.day))
        self.remove(animal)

    def addDeadCreature(self, deadCreature:DeadCreature):
        self.deadCreatures.append(deadCreature)
        x,y = deadCreature.getCoords()
        self.getGrid()[x][y].addDeadCreature(deadCreature)
        return self.deadCreatures

    def addGroup(self, group:SocialGroup):
        x,y = group.getCoords()

        if isinstance(group, Herd):
            self.totErbast += group.numComponents
            self.creatures["Erbast"].extend(group.getComponents())
            self.getGrid()[x][y].addGroup(group)

        if isinstance(group, Pride):
            self.totCarviz += group.numComponents    
            self.creatures["Carviz"].extend(group.getComponents())
            self.getGrid()[x][y].addGroup(group)

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
            
        logging.error(f"animal: {animal}, at coords {animal.getCoords()}, is not present in any cell")
                                                                
    def removeGroup(self, group:SocialGroup):
        """"""
        if not isinstance(group, SocialGroup):
            raise TypeError(f"{group} is not a social Group")
        
        x,y = group.getCoords()

        if isinstance(group, Herd):
            if all(el in self.creatures["Erbast"] for el in group.getComponents()):
                self.totErbast -= group.numComponents
                self.creatures["Erbast"] = [erb for erb in self.creatures["Erbast"] if erb not in group.getComponents()]
                self.getGrid()[x][y].removeHerd(group)
            else:
                raise Exception(f"not all components of {group} are in the creatures list")

        elif isinstance(group, Pride):
            if all(el in self.creatures["Carviz"] for el in group.getComponents()):
                self.totCarviz -= group.numComponents
                self.creatures["Carviz"] = [carv for carv in self.creatures["Carviz"] if carv not in group.getComponents()]
                self.getGrid()[x][y].removePride(group)
            else:
                raise Exception(f"not all components of {group} are in the creatures list")

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
        
        
        for o, c in nextCoords.items():
            if isinstance(o, SocialGroup) and len(o.getComponents()) < 2:
                logging.warning(f"SocialGroup {o} has less than 2 components, removing it")
                self.remove(o)
                continue
            self.remove(o)
            self._changeCoords(o, c)
            self.add(o)
        
    def _changeCoords(self, obj:Species,newCoords:tuple):
        """helper func to change the coords of an animal or a socialgroup"""
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
                c1.changeEnergy(-c2Energy)
                p1Carvizes.sort(key = lambda x : x.getEnergy())
            elif c1Energy < c2Energy:
                self.creatureDeath(c1)
                p1Carvizes.pop()
                c2.changeEnergy(-c1Energy)
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

        totHunts = 0
        succesfulHunts = 0

        cellHunters = self.getCellSpeciesDict(self.getPrides() + self.getAloneCarviz())
        cellHerds = self.getCellSpeciesDict(self.getHerds())
        cellErbasts = self.getCellSpeciesDict(self.getAloneErbasts())

        # Log energies of carvizes, including those in prides
        logging.info("CARVIZES ENERGIES\n")
        for coords, hunters in cellHunters.items():
            for hunter in hunters:
                if isinstance(hunter, Carviz):
                    logging.info(f"{hunter} at {coords} has energy: {hunter.getEnergy()}")
                elif isinstance(hunter, Pride):
                    for carviz in hunter.getComponents():
                        logging.info(f"{carviz} in Pride at {coords} has energy: {carviz.getEnergy()}")

        for coords in cellHunters:
            if coords in cellHerds or coords in cellErbasts:

                # obtain the strongest erbast and the pride
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
                    hunterStrength = hunter.getGroupEnergy() * numPrideComponents * hunter.getGroupSociality() + 1
                elif isinstance(hunter, Carviz):
                    hunterStrength = hunter.getEnergy() * (2 - hunter.getSocialAttitude()) + 1

                erbastLuck = random.randint(1,3)
                huntProbability = self._hunt_probability(erbastEnergy, hunterStrength) * erbastLuck

                totHunts += 1

                while attempts < 5: # 5 assaults

                    if isinstance(hunter, Pride):

                        if random.random() < huntProbability: # Pride wins
                            self.creatureDeath(strongestErbast)
                            logging.info(f"{strongestErbast} has been killed by {hunter}")

                            succesfulHunts += 1

                            # energy sharing
                            individualShare = (erbastEnergy // numPrideComponents) + 5
                            hunter.changeEnergy(individualShare)
                            hunter.changeGroupSociality(0.1)

                            # the hungriest carviz gets the spare energy
                            spareEnergy = erbastEnergy % numPrideComponents
                            hungriestCarviz = min(hunter.getComponents(), key = lambda x : x.getEnergy())
                            hungriestCarviz.changeEnergy(spareEnergy) 

                            if coords in cellHerds:
                                if len(herd.getComponents()) > 1 and attempts < 4:
                                    strongestErbast = max(herd.getComponents(), key = lambda x : x.getEnergy())
                                    totHunts += 1
                                else:
                                    break
                            else:
                                break
                        else:
                            hunter.changeGroupSociality(-0.1)
                            attempts += 1
                            anyAlive = any(self.changeEnergyAndHandleDeath(hunter, -2).values())
                            logging.info(f"{hunter} failed to hunt {strongestErbast}, attempt {attempts}. any Alive?: {anyAlive}")
                            if not anyAlive:
                                break
                    
                    elif isinstance(hunter, Carviz):
                        
                        if random.random() < huntProbability: # death
                            self.creatureDeath(strongestErbast)
                            succesfulHunts += 1
                            logging.info(f"{strongestErbast} has been killed by {hunter}")
                            hunter.changeEnergy(erbastEnergy)
                            hunter.socialAttitude -= 0.1
                            if coords in cellHerds:
                                if len(herd.getComponents()) > 1 and attempts < 4:
                                    strongestErbast = max(herd.getComponents(), key = lambda x : x.getEnergy())
                                    totHunts += 1
                                else:
                                    break
                            else:
                                break
                        else:
                            attempts += 1
                            hunter.socialAttitude += 0.1
                            alive = self.changeEnergyAndHandleDeath(hunter, -2)[hunter]
                            logging.info(f"{hunter} failed to hunt {strongestErbast}, attempt {attempts}. alive?: {alive}")
                            if not alive:
                                break

        # Log energies of carvizes, including those in prides again after hunting
        logging.info("CARVIZES ENERGIES AFTER HUNTING\n")
        for coords, hunters in cellHunters.items():
            for hunter in hunters:
                if isinstance(hunter, Carviz):
                    logging.info(f"{hunter} at {coords} has energy: {hunter.getEnergy()}")
                elif isinstance(hunter, Pride):
                    for carviz in hunter.getComponents():
                        logging.info(f"{carviz} in Pride at {coords} has energy: {carviz.getEnergy()}")

        return totHunts, succesfulHunts

    def nextDay(self):
        """The days phase happens one after the other until the new day"""

        self.day += 1

        logging.info(f"DAY {self.day}\n")
        logging.info(f"creatures: {self.creatures}")
        logging.info(f"deadCreatures: {self.deadCreatures}")
        logging.info(f"herds: {self.getHerds()}")
        logging.info(f"prides: {self.getPrides()}\n")
        logging.info(f"totErbast: {self.totErbast}")
        logging.info(f"totCarviz: {self.totCarviz}")
        logging.info(f"len Creatures Erbasts: {len(self.creatures['Erbast'])}")
        logging.info(f"len Creatures Carviz: {len(self.creatures['Carviz'])}")

        grid = self.getGrid()
        cells = grid.reshape(-1)
        landCells = [landC for landC in cells if isinstance(landC,LandCell)]

        # 3.1 - GROWING -----------------------------------------------------------------------------------------------

        for cell in landCells:
            cell.growVegetob()

        # 3.2 - MOVEMENT -----------------------------------------------------------------------------------------------

        logging.info("MOVEMENT PHASE\n")

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

                if isinstance(c, (Pride, Carviz)):
                    aliveDict = self.changeEnergyAndHandleDeath(c, ENERGY_LOSS_C)
                    
                elif isinstance(c, (Erbast, Herd)):
                    aliveDict = self.changeEnergyAndHandleDeath(c, ENERGY_LOSS_E)
                else:
                    raise TypeError(f"{c} is not a Carviz, Erbast, Pride or Herd")

                if isinstance(c, SocialGroup) and sum(aliveDict.values()) < 2: # 0 or 1 alive
                    logging.info(f"Of {c}, all except {sum(aliveDict.values())} are alive during movement due to starvation")
                    nextCoords.pop(c)
                else:
                    deadC = [creature for creature,alive in aliveDict.items() if not alive]
                    for d in deadC:
                        if d in nextCoords:
                            nextCoords.pop(d)
                
        logging.info(f"NextCoords:\n{pprint.pformat(nextCoords)}")
        self.move(nextCoords)


        # 3.3 - GRAZING -----------------------------------------------------------------------------------------------

        stayingErbast = [e for e in stayingCreatures if isinstance(e, Erbast) or isinstance(e,Herd)]
        for e in stayingErbast:
            self.graze(e) #this includes cell vegetob reduction, herd and individual energy increase

        # 3.4 - STRUGGLE -----------------------------------------------------------------------------------------------

        # Erbasts are automatically merged in Herds from LandCell internal updates when trying to add them

        # two important things are going to happen: Alone carvizes joining a pride and pride struggling
        # the order here matters and would promote or not change the win of the group with the higher social Attitude
        # the order will be random

        logging.info("STRUGGLE PHASE\n")

        orderCarvizJoins = random.randint(0,1)

        if orderCarvizJoins == 0:
            self.joinCarvizesToPride()
            self.struggle()
        elif orderCarvizJoins == 1:
            self.struggle()
            self.joinCarvizesToPride()
        
        # 3.4 - HUNT -----------------------------------------------------------------------------------------------

        logging.info("HUNT PHASE\n")

        totHunts, succesfulHunts =  self.hunt()

        # 3.5 - SPAWNING -----------------------------------------------------------------------------------------------

        for c in self.creatures["Erbast"] + self.creatures["Carviz"]:
            alive, offsprings = c.ageStep()
            if offsprings:
                for offspring in offsprings:
                    self.add(offspring)
            if not alive:
                self.creatureDeath(c)
        

        # Log cells with Erbasts
        logging.info("LANDCELLS WITH ERBASTS\n")
        for cell in landCells:
            erbast_list = cell.getErbastList()
            if erbast_list:
                logging.info(f"LandCell {cell.getCoords()} has Erbasts: {erbast_list}")
                if len(erbast_list) != cell.numErbast:
                    logging.error(f"LandCell {cell.getCoords()} has {cell.numErbast} Erbasts but the list has {len(erbast_list)}")
                    raise Exception(f"LandCell {cell.getCoords()} has {cell.numErbast} Erbasts but the list has {len(erbast_list)}")

        logging.info("LANDCELLS WITH CARVIZES\n")
        for cell in landCells:
            carviz_list = cell.getCarvizList()
            if carviz_list:
                logging.info(f"LandCell {cell.getCoords()} has Carvizes: {carviz_list}")

        self.computeStatistics(totHunts, succesfulHunts)

        logging.warning(f"Statistics for day {self.day}:")
        for stat, values in self.statistics.items():
            logging.warning(f"{stat}: {values[-1]}")

        return self.getGrid()
    
class WorldGrid():
    """
    class that handles the creation of the islands, initial flora and fauna,
    and aquatic zones its main attribute is grid
    """
    def __fbmNoise(self, n, threshold = 0.2, seed = None, octaves=8, persistence=0.4, lacunarity=1.8, scale=40.0, dynamic=False):
        """ Method to generate island like maps. Returns a numpy grid of zeros and 255 """
        # print(dynamic)
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
                    # logging.info(dynamic_treshold)
                    grid[i][j] = 1 if grid[i][j] > dynamic_treshold else 0
        else:
            grid = np.where(grid > threshold, 1, 0)
                
        return grid

    def __init__(self, type = "fbm", threshold = 0.2, seed=None, octaves=8, persistence=0.4, lacunarity=1.8, scale=40.0, dynamic=False):
        self.grid = self.createWorld(type, threshold, seed, octaves, persistence, lacunarity, scale, dynamic)
    # so that we can crate different types of initial setups
    def createWorld(self, typology = "fbm", threshold = 0.2, seed=None, octaves=8, persistence=0.4, lacunarity=1.8, scale=40.0, dynamic=False):
        """
        Initialize the world
        Vegetob density starts at around 25
        """
        
        if typology == "fbm":
            values_grid = self.__fbmNoise(NUMCELLS, threshold, seed=seed, octaves=octaves, persistence=persistence, lacunarity=lacunarity, scale=scale, dynamic=dynamic)
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
        self.deadCreatures = []
        self.herd = None
        self.prides = []
        self.numErbast = 0
        self.numCarviz = 0
        self.numDeadCreatures = 0

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

        logging.info(f"Trying to add at coords: {self.coords}, the animal: {animal}, "
             f"numErbast: {self.numErbast}, numCarviz: {self.numCarviz}, herd: {self.herd}")
        
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

    def addDeadCreature(self, deadCreature:DeadCreature):
        """Add a dead creature to the cell"""
        if not isinstance(deadCreature, DeadCreature):
            raise TypeError(f"{deadCreature} is not a DeadCreature")
        self.deadCreatures.append(deadCreature)
        self.numDeadCreatures += 1

    def removeAnimal(self, animal:'Animal'): 
        """Remove an animal from the inhabitants list"""

        logging.info(f"Trying to remove at coords: {self.coords}, the animal: {animal}, "
             f"numErbast: {self.numErbast}, numCarviz: {self.numCarviz}, herd: {self.herd}")


        if isinstance(animal, Erbast):
            if animal in self.creatures["Erbast"]:

                if self.numErbast == 0 and not self.herd:
                    raise Exception(f"{animal} is not present in the cell {self}, hence it can't be removed. The cell is empty")
                
                elif self.numErbast == 1 and not self.herd:
                    self.numErbast -= 1
                    self.creatures["Erbast"].remove(animal)

                elif self.numErbast == 2 and self.herd:
                    presentHerd = self.herd
                    result = presentHerd.loseComponent(animal)
                    individuals = result["individuals"]
                    self.creatures["Erbast"].clear()
                    self.numErbast = 0 # as addAnimal will increment it
                    self.herd = None
                    logging.info(f"trying to remove {animal} from the cell {self}, herd: {self.herd}, numErbast: {self.numErbast}. The result of loseComponent is: {result}")
                    self.addAnimal(individuals[1])

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
                pride = animal.getSocialGroup()
                if pride:
                    pride.loseComponent(animal)
                self.creatures["Carviz"].remove(animal)
                
                self.numCarviz -= 1

    def addGroup(self, group:'SocialGroup'):
        """
        add a Herd or a Pride to the landCell and eventually resolve conflicts / join groups
        """

        logging.info(f"trying to add group {group} at coords: {self.coords}, numErbast: {self.numErbast}, numCarviz: {self.numCarviz}, herd: {self.herd}")

        if isinstance(group, Herd):
            if self.herd is not None:
                self.numErbast += group.numComponents
                self.creatures["Erbast"].extend(group.getComponents())
                self.herd.joinGroups(group)
            else:
                if self.numErbast == 1:
                    presentAnimal = self.creatures["Erbast"][0]
                    self.removeAnimal(presentAnimal)
                    group.addComponent(presentAnimal)
                self.numErbast += group.numComponents
                self.creatures["Erbast"].extend(group.getComponents())
                self.herd = group

        elif isinstance(group, Pride): # pride logic handled by struggle
            self.numCarviz += group.numComponents
            self.prides.append(group)
            self.creatures["Carviz"].extend(group.getComponents())

    def removeHerd(self, herd:'Herd'):
        """Remove the herd from the landCell"""

        logging.info(f"Trying to remove herd {herd} at coords: {self.coords}, numErbast: {self.numErbast}, "
             f"numCarviz: {self.numCarviz}, herd: {self.herd}")


        if self.herd is not None:
            self.creatures["Erbast"] = [erb for erb in self.creatures["Erbast"] if erb not in herd.getComponents()]
            self.numErbast -= self.herd.numComponents
            if self.numErbast < 2:
                self.herd = None
            else:
                if len(self.creatures["Erbast"]) == 0:
                    logging.warning(f"herd: {herd} has been removed from the cell {self}, numErbast: {self.numErbast}, but {self.creatures['Erbast']}")
                self.herd = Herd(self.creatures["Erbast"]) #form a new herd with the remaining erbasts TODO


    def removePride(self, pride:'Pride'):
        """Remove the pride from the landCell"""

        logging.info(f"Trying to remove pride at coords: {self.coords}, numErbast: {self.numErbast}, "
             f"numCarviz: {self.numCarviz}, herd: {self.herd}")


        self.creatures["Carviz"] = [car for car in self.creatures["Carviz"] if car not in pride.getComponents()]
        self.numCarviz -= pride.numComponents
        self.prides.remove(pride)

    def getErbastList(self):
        """Get a list of all Erbast inhabitants in the cell"""
        return self.creatures["Erbast"]

    def getCarvizList(self):
        """Get a list of all Carviz inhabitants in the cell"""
        return self.creatures["Carviz"]
    
    def getDeadCreaturesList(self):
        """Get a list of all DeadCreatures in the cell"""
        return self.deadCreatures

    def getCellType(self):
        return "land"

    def getHerd(self):
        return self.herd
    
    def getPrides(self):
        return self.prides
    
    def __repr__(self):
        return f"LandCell {self.coords}"
