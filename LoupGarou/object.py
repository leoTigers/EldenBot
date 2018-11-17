import discord
import random
from LoupGarou.constant import OPTION


class Player:
    def __init__(self, role, member, plid):
        self.life = True
        self.role = role()
        self.member = member
        self.name = member.name
        self.id = plid
        self.love = None
        self.game = None
    async def kill(self, reason="none"):
        self.life = False
        self.game.alive.remove(self)
        return await self.game.announce('death_' + reason, author=self.member)

class Announce:
    def __init__(self, game, line):
        self.game = game
        self.announce = line[0]
        self.color = int(line[1], base=16)
        self.title = line[3] if line[3] else None
        self.texts = [ann for ann in line[4:] if ann]
    async def send(self, author=None, mp=False, image=None, title_args=[], desc_args=[]):
        channel = author if mp else self.game.channel
        em = discord.Embed(title=self.title.format(*title_args), colour=self.color,
                           description=random.choice(self.texts).format(*desc_args))
        if author:
            em.set_author(name=author.name, icon_url=author.avatar_url)
        if image:
            em.set_thumbnail(url=image)
        channel = author if mp else self.game.channel
        return await channel.send(embed=em)

from LoupGarou.announce import load_announce

class Game:
    def __init__(self, mj, channel):
        self.mj = mj
        self.channel = channel
        self.option = OPTION
        self.players = None
        self.alive = None
        self.lovers = []
        self.announces = load_announce(self)
    def _set_players(self, players):
        self.players = players
        self.alive = players
    async def announce(self, ann, **kwarg):
        await self.announces[ann].send(**kwarg)


def is_alive(function, role):
    async def wrapper(game):
        for player in game.alive:
            if player.role == role:
                await function(role, player)
    return wrapper
