from object import Player
from constant import *
import discord

option = {"reaveal_role_at_death": True}

async def lg_start(message, mj, argv):
    #create players list
    players_list = create_plist(message, mj)
    #option
    await message.channel.send("```diff\n{}```".format("{} {} : {}".format('+' if i else '-', i, j)
                                                       for i, j in option.items()))
    #role distribution

    #create game object
    lg = LoupGarou()

async def create_plist(message, mj):
    players_list = [mj]
    em = discord.em(title=START_PL_TITLE, description=)
    msg = await message.channel.send(embed=em)

    def check(reaction, user):
        ok = str(reaction.emoji) == OK_EMOJI
        next = str(reaction.emoji) == NEXT_EMOJI
        return reaction.message == msg and (ok or next) and user != client.user

    while True:
        #update players_list
        players_list = []
        for reaction in msg.reactions:
            if str(reaction.emoji) == OK_EMOJI:
                async for user in reaction.users():
                    if user != client.user:
                        players_list.append(user)
        for player in players_list:
            em = discord.Embed(title=START.START_PL_TITLE,
                               description="\n".join(["- " + i.name for i in players_list]))
        reaction, user = await client.wait_for('reaction_add', check=check)
        if str(reaction.emoji) == NEXT_EMOJI and user == mj:
            break
        if len(players_list) >= 6:
            try: await msg.add_reaction(NEXT_EMOJI)
            except: pass
    em.set_footer(text="Les joueurs ont été lock")
    await msg.edit(embed=em)
    return players_list
