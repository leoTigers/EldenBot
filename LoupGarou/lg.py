from object import Player
from constant import *
import discord

async def lg_start(message, mj, argv):
    players_list = [mj]
    em = discord.em(title=START_PL_TITLE, description=)
    msg = await message.channel.send(embed=em)
    for player in player_list:
        em.discord.em(title=START.START_PL_TITLE,
                      description="\n".join(["- " + i.name for i in players_list])) 
