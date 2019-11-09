import random
from LoupGarou.Loading.announce import load_images

class Role:
    def __init__(self, images):
        self.name = self.__str__()
        self.image = random.choice(images[str(self)])
    def __eq__(self, other):
        return str(other) in [str(self), self.__class__.__name__]

class Werewolf(Role):
    def __str__(self):
        return "loup-garou"

class Villager(Role):
    def __str__(self):
        return "villageois"

class Seer(Role):
    def __str__(self):
        return "voyante"

class Witch(Role):
    def __init__(self, images):
        super().__init__(images)
        self.heal = 1
        self.poison = 1
    def __str__(self):
        return "sorcière"

class Cupidon(Role):
    def __str__(self):
        return "cupidon"

class Hunter(Role):
    def __str__(self):
        return "chasseur"
