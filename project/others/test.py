class uomo:
    def __init__(self):
        pass

class ometto(uomo):
    def __init__(self):
        pass

luchino = ometto() 

print(isinstance(luchino, uomo))