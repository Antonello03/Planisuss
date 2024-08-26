class Species:

    def __init__(self):
        pass

class Vegetob(Species):
    
    def __init__(self, density = 0):
        self.density = density

    def __repr__(self):
        return "Vegetob"

class Erbast(Species):

    def __init__(self):
        super().__init__(self)

    def __repr__(self):
        return "Erbast"

class Carvis(Species):

    def __init__(self):
        super().__init__(self)

    def __repr__(self):
        return "Carviz"

class SocialGroup:
    """
    Holds knowledge about the environment
    """

    def __init__(self, components):
        self.components = components

    def getComponents(self):
        return self.components

class Herd(SocialGroup):

    def __init__(self, components):
        super().__init__(self, components)
        pass

class Pride(SocialGroup):

    def __init__(self, components):
        super().__init__(self, components)
        pass