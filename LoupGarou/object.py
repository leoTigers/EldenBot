import discord

class LoupGarou:
    def __init__(self, mj, player_list):
        self.mj = mj
        self.players = player_list
        self.alive = player_list

class Player:
    def __init__(self, role, member, plid):
        self.life = True
        self.role = role
        self.member = member
        self.name = member.name
        self.id = plid
        self.love = None
        self.game = None
    async def kill(self, reason="une source inconnue"):
        self.life = False
        em = discord.Embed(title = "{} a été tué par {}".format(self.name, reason))
