class Role:
    def __init__(self):
        self.name = self.__str__(self)
    def __eq__(self, other):
        return str(self) == str(other)

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
    def __init__(self):
        super().__init__()
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
