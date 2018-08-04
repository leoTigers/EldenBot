#!/usr/bin/python3
from pantheon import pantheon
import time
import discord
import asyncio
import logging
import traceback
import json

with open("../private/rgapikey") as key:
    panth = pantheon.Pantheon("euw1", key.read(), True)
    
def load_data():
    try:
        print("loading data ...")
        with open("../private/circus.data", 'r') as fd:
            data = json.loads(fd.read())
    except:
        print("IMPOSSIBLE DE LOAD ../private/circus.data")
        data = {}
    try:
        print("loading summoners ...")
        with open("../private/summoners.data", 'r') as fd:
            summ = json.loads(fd.read())
    except:
        print("IMPOSSIBLE DE LOAD ../private/summoners.data")
        summ = {}
    return (data, summ)

logging.basicConfig(level=logging.INFO)
client = discord.Client()
data, summoners = load_data()
start_msg = None
FORUM_GUILD_ID = 367683573014069249
CIRCUS_GUILD_ID = 466950374243303434
REG_CHANNEL_ID = 466961756393046017
LINK_CHANNEL_ID = 474254945764376577
MSG_ID = 474227467414929420
ALREADY_VERIFIED = "{} est déjà vérifié sur le discord du forum (SummonerId : {})"
FORBIDDEN = "Désolé, seuls les Organisateurs peuvent utiliser cette commande."
MISSING_ARG = "Erreur : Argument manquant"
NOT_FOUND = "Membre non trouvé"
FORCE_REGISTED = "{} a été inscrit de force à l'évenement {} par {}"
FORCE_UNREGISTED = "{} a été désinscrit de force à l'évenement {} par {}"
PRE_REGISTED = "{} a été préinscrit à l'évenement {} par {}"
REREGISTED = "{} s'est fait reregister sur l'évenement {}"
READYCHECK = "__**Vérification de présence !**__\n\nprésent: {}\nabsent: {}\n\ntemps restant: {}"
def TIME(x): return ("{}:{}".format(int(x) // 60, str(int(x) % 60).zfill(2)))
def MENTION(discord_id): return ("<@{}>".format(discord_id))

@client.event
async def on_ready():
    print("Connected (cirque de l'invocateur)")
    await update_msg()
    for member in client.get_guild(CIRCUS_GUILD_ID).members:
        await verif(member)

@client.event
async def on_member_join(member):
    if member.guild.id == CIRCUS_GUILD_ID:
        await verif(member)

async def verif(member):
    forum = client.get_guild(FORUM_GUILD_ID)
    lie = discord.utils.get(member.guild.roles, id=474254455194517504)
    if lie not in member.roles:
        fmember = forum.get_member(member.id)
        if "Vérifié" in [role.name for role in fmember.roles]:
            data = await panth.getSummonerByName(fmember.display_name)
            name, summId = data['name'], data['id']
            summoners[str(member.id)] = summId
            link_channel = client.get_channel(LINK_CHANNEL_ID)
            try:
                await member.edit(nick=name)
            except discord.errors.Forbidden:
                pass
            await member.add_roles(lie, reason="Vérifié sur le discord du forum")
            await link_channel.send(ALREADY_VERIFIED.format(str(member), summId))
            save_summ()
    else:
        data = await panth.getSummonerByName(member.display_name)
        try:
            await member.edit(nick=data["name"])
        except:
            pass

@client.event
async def on_message(message):
    if message.guild.id == CIRCUS_GUILD_ID:
        try:
            if message.channel.id == LINK_CHANNEL_ID and \
               "Lié" not in [x.name for x in message.guild.roles]:
                pass
            if message.content.startswith('+') and message.channel.id == REG_CHANNEL_ID:
                await register(message)
            if message.content.startswith('-') and message.channel.id == REG_CHANNEL_ID:
                await unregister(message)
            if message.content.startswith('/'):
                av = message.content.split(' ')
                while '' in av : av.remove('')
                if av[0] == "/start" : await start_game(message, av)
                if av[0] == "/create" : await create(message, av)
                if av[0] == "/delete" : await delete(message, av)
                if av[0] == "/preregister" : await pre_register(message, av)
                if av[0] == "/unpreregister" : await unpre_register(message, av)
                if av[0] == "/reregister" : await reregister(message, av)
                if av[0] == "/forceregister" : await force_register(message, av)
                if av[0] == "/forceunregister" : await force_unregister(message, av)
        except Exception:
            await message.channel.send("```diff\n-[Erreur]\n" + traceback.format_exc() + "```")


async def is_authorised(message):
    perm = message.author.guild_permissions
    if perm.administrator or perm.manage_channels or perm.manage_guild:
        return True
    await message.channel.send(FORBIDDEN)
    return False


async def register(message):
    event_name = message.content.split('+')[1].lower()
    if event_name not in data.keys():
        await message.channel.send("L'évenement n'existe pas.")
        return False
    discord_id = message.author.id
    if discord_id in data[event_name]:
        await message.channel.send("Vous êtes déjà inscrit.")
        return False
    data[event_name].append(discord_id)
    await message.channel.send("{} s'est inscrit à l'évenement {}".format(
        MENTION(discord_id), event_name.capitalize()))
    await update_msg()

    
async def unregister(message):
    event_name = message.content.split('-')[1].lower()
    if event_name not in data.keys():
        await message.channel.send("L'évenement n'existe pas.")
        return False
    discord_id = message.author.id
    if discord_id not in data[event_name]:
        await message.channel.send("Vous êtes déjà désinscrit.")
        return False
    data[event_name].remove(discord_id)
    await message.channel.send("{} s'est désinscrit à l'évenement {}".format(
        MENTION(discord_id), event_name.capitalize()))
    await update_msg()

async def pre_register(message, av):
    if not await is_authorised(message):
        return False
    if len(av) < 3:
        await message.channel.send(MISSING_ARG)
        return False
    name = av[1]
    event_name = av[2].lower()
    if event_name not in data.keys():
        await message.channel.send("L'évenement n'existe pas.")
        return False
    if name in data[event_name]:
        await message.channel.send("Le membre est déjà préinscrit")
        return False
    data[event_name].append(name)
    await message.channel.send(PRE_REGISTED.format(name,
                                                   event_name.capitalize(),
                                                   message.author.mention))
    await update_msg()
    await message.delete()

async def reregister(message, av):
    if not await is_authorised(message):
        return False
    if len(av) < 3:
        await message.channel.send(MISSING_ARG)
        return False
    name = av[1]
    discord_id = get_member_id(message, av[2])
    if not discord_id:
        await message.channel.send(NOT_FOUND)
        return False
    for event, pl in data.items():
        for i in range(len(pl)):
            if pl[i] == name:
                pl[i] = discord_id
                await message.channel.send(REREGISTED.format(name,
                                                             event.capitalize()))

async def unpre_register(message, av):
    if not await is_authorised(message):
        return False
    if len(av) < 3:
        await message.channel.send(MISSING_ARG)
        return False
    name = av[1]
    event_name = av[2].lower()
    if event_name not in data.keys():
        await message.channel.send("L'évenement n'existe pas.")
        return False
    if name not in data[event_name]:
        await message.channel.send("Le membre est déjà préinscrit")
        return False
    data[event_name].remove(name)
    await message.channel.send(FORCE_UNREGISTED.format(name,
                                                       event_name.capitalize(),
                                                       message.author.mention))
    await update_msg()
    await message.delete()
    
def get_member_id(message, txt):
    try:
        id = int(txt)
        return (id)
    except:
        try:
            member = message.guild.get_member_named(txt)
            return (member.id)
        except:
            return None

    
async def force_register(message, av):
    if not await is_authorised(message):
        return False
    if len(av) < 3:
        await message.channel.send(MISSING_ARG)
        return False
    discord_id = get_member_id(message, av[1])
    if not discord_id:
        await message.channel.send(NOT_FOUND)
        return False
    event_name = av[2].lower()
    if event_name not in data.keys():
        await message.channel.send("L'évenement n'existe pas.")
        return False
    if discord_id in data[event_name]:
        await message.channel.send("Le membre est déjà inscrit")
        return False
    data[event_name].append(discord_id)
    await message.channel.send(FORCE_REGISTED.format(MENTION(discord_id),
                                                     event_name.capitalize(),
                                                     message.author.mention))
    await update_msg()
    await message.delete()

async def force_unregister(message, av):
    if not await is_authorised(message):
        return False
    if len(av) < 3:
        await message.channel.send(MISSING_ARG)
        return False
    discord_id = get_member_id(message, av[1])
    if not discord_id:
        await message.channel.send(NOT_FOUND)
        return False
    event_name = av[2].lower()
    if event_name not in data.keys():
        await message.channel.send("L'évenement n'existe pas.")
        return False
    if discord_id not in data[event_name]:
        await message.channel.send("Le membre est déjà désinscrit")
        return False
    data[event_name].remove(discord_id)
    await message.channel.send(FORCE_UNREGISTED.format(MENTION(discord_id),
                                                       event_name.capitalize(),
                                                       message.author.mention))
    await update_msg()
    await message.delete()
    
    
async def create(message, av):
    if not await is_authorised(message):
        return False
    if len(av) < 2:
        await message.channel.send(MISSING_ARG)
        return False
    event_name = av[1].lower()
    if event_name in data.keys():
        await message.channel.send("L'évenement existe déjà.")
        return False
    data[event_name] = []
    await update_msg()
    await message.channel.send("evenement ajouté")
    await message.delete()


async def delete(message, av):
    if not await is_authorised(message):
        return False
    if len(av) < 2:
        await message.channel.send(MISSING_ARG)
        return False
    event_name = av[1].lower()
    if event_name not in data.keys():
        await message.channel.send("L'évenement n'existe pas.")
        return False
    del data[event_name]
    await update_msg()
    await message.channel.send("evenement supprimé")
    await message.delete()

    
async def update_msg():
    save_data()
    channel = client.get_channel(REG_CHANNEL_ID)
    msg = await channel.get_message(MSG_ID)
    txt = "__Liste des inscrits__:\n\n"
    for event, pl in data.items():
        txt += "**{}**:\n{}\n\n".format(
            event.capitalize(),
            ", ".join([MENTION(i) if str(i).isdigit() else i for i in pl ]))
    await msg.edit(content=txt)

async def start_game(message, av):
    global start_msg
    await message.delete()
    channel = client.get_channel(REG_CHANNEL_ID)
    game = av[1].lower()
    timer = time.time() + (360 if len(av) == 2 else int(av[2])) 
    start_msg = await message.channel.send(
        READYCHECK.format("",
                          ", ".join([MENTION(i) for i in data[game]]),
                          TIME(timer - time.time())))
    await start_msg.add_reaction("✔")
    while timer - time.time() >= 0 :
        try:
            start_msg = await channel.get_message(start_msg.id)
            ready = await start_msg.reactions[0].users().flatten()
            ready = [i.id for i in ready]
            await start_msg.edit(content=\
                READYCHECK.format(", ".join([MENTION(i) for i in data[game] if i in ready]),
                                  ", ".join([MENTION(i) for i in data[game] if i not in ready]),
                                  TIME(timer - time.time())))
        except:
            pass
        await asyncio.sleep(0.5)
    print("done")

def save_data():
    with open("../private/circus.data", 'w') as fd:
        fd.write(json.dumps(data))

def save_summ():
    with open("../private/summoners.data", 'w') as fd:
        fd.write(json.dumps(summoners))

with open("../private/token") as fd:
    client.run(json.load(fd))
