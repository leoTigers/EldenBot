from object import Player
from constant import *
import discord
import random

option = {"reaveal_role_at_death": True}

async def lg_start(message, mj, argv):
    game = Game(mj, message.channel)
    #create players list
    players_list = await create_plist(message, mj)
    #option
    await game.channel.send("```diff\n{}```".format("{} {} : {}".format('+' if i else '-', i, j)
                                                    for i, j in option.items()))
    #role distribution
    players = await distrib_role(players_list, game)
    game._set_players(players)
    #create game object


async def distrib_role(players_list, game):
    players = []
    role_list  = ROLE_LIST[len(players_list):]
    plid = 0
    while players_list:
        plid += 1
        player_index = random.randint(0, len(players_list) - 1)
        role_index = random.randint(0, len(players_list) - 1)
        new_player = Player(role_list[role_index], players_list[players_index])
        players.append(new_player)
        del role_list[role_index], players_list[players_list]
        await game.announce("announce_" + str(new_player.role),
                            author=new_player.member, mp=True)
    return players

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
