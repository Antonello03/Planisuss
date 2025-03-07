import random
from interface import Interface
from world import Environment
from creatures import Erbast, Carviz, Herd, Pride

environment = Environment()
animation = Interface(env = environment)

def initializePopulation(environment, type:str = "test1", nErb = 10, nCarv = 10):
    grid_shape = environment.getGrid().shape
    land_cells = [(x, y) for x in range(grid_shape[0]) for y in range(grid_shape[1])
                  if environment.isLand(x, y)]
    print(land_cells)

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

    if type == "random":
        for i in range(nErb):
            (x, y) = random.choice(land_cells)
            # coords = (random.randint(20,30), random.randint(20,30))
            erb = Erbast((x, y), SocialAttitude = random.random())
            environment.add(erb)

        for i in range(nCarv):
            (x, y) = random.choice(land_cells)
            # coords = (random.randint(20,30), random.randint(20,30))
            carv = Carviz((x, y), SocialAttitude = random.random())
            environment.add(carv)

# random.seed(1)
initializePopulation(environment, "random", 20, 20)

animation.run_simulation()