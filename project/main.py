import random
from interface import Interface
from world import Environment
from creatures import Erbast, Carviz, Herd, Pride

environment = Environment()
animation = Interface(env = environment)

def initializePopulation(type:str = "test1", nErb:int = 10, nCarv:int = 10):

    if type == "test1":
        erb1 = Erbast((25,25), energy=100, name="schiavo 1")
        erb2 = Erbast((25,25), energy=5, name="schiavo 2")
        erb3 = Erbast((25,25), energy=5, name="schiavo 3")
        herd1 = Herd([erb1,erb2,erb3])
        environment.add(herd1)

        erbOther = Erbast((24,25), energy=100, name="schiavo 4")
        erbOther2 = Erbast((24,25), energy=5, name = "schiavo 5")
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

    if type == "random":
        for i in range(nErb):
            coords = (random.randint(20,30), random.randint(20,30))
            erb = Erbast(coords, SocialAttitude = random.random())
            environment.add(erb)

        for i in range(nCarv):
            coords = (random.randint(20,30), random.randint(20,30))
            carv = Carviz(coords, SocialAttitude = random.random())
            environment.add(carv)

random.seed(1)
initializePopulation("random", 20, 20)

animation.run_simulation()


# TWO BIG PROBLEMS
# CARVIZES DIYNG MULTIPLE TIMES - MAYBE SOLVED
# MODIFIED MOVECHOICE BUT KNOW PRIDES ARE NOT CORRECTLY HANDLED
# ADDING ANIMALES WITHOUT COORDS UPDATE

# MAIN PROBLEM IS THAT LANDCELL KEEPS HOLDING DEAD ERBASTS (AND CARVIZES ?)
