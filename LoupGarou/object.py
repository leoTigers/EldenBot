import discord

class Player:
    def __init__(self, role, member, plid):
        self.life = True
        self.role = role
        self.member
        self.name = member.name
        self.id = plid
        self.love = None
    async def kill(self, reason="une source inconnue"):
        self.life = False
        em = discord.Embed(title = "{} a été tué par {}".format(self.name, reason))
    
        
        
