class Planet:

    def __init__(self, name, base, depth):
        self.name = name
        self.base = base
        self.depth = depth

    def get_tone(self):

        return [self.base, self.depth]

    def getCalculatedTone(self, sinVal):
        return self.base + sinVal * self.depth

class Mercury(Planet):
    def __init__(self):
        super().__init__("Mercury", 1500, 300)

class Venus(Planet):
    def __init__(self):
        super().__init__("Venus", 1800, 400)

class Earth(Planet):
    def __init__(self):
        super().__init__("Earth", 2000, 500)

class Mars(Planet):
    def __init__(self):
        super().__init__("Mars", 2200, 600)

class Jupiter(Planet):
    def __init__(self):
        super().__init__("Jupiter", 2500, 700)

class Saturn(Planet):
    def __init__(self):
        super().__init__("Saturn", 2700, 800)

class Uranus(Planet):
    def __init__(self):
        super().__init__("Uranus", 2900, 900)

class Neptune(Planet):
    def __init__(self):
        super().__init__("Neptune", 3100, 1000)