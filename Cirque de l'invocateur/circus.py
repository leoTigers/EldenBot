#!/usr/bin/python3
import discord
import asyncio
import logging
import traceback
import json

def load_data():
    try:
        print("loading data ...")
        with open("../private/circus.data", 'r') as fd:
            return (json.loads(fd.read()))
    except:
        print("IMPOSSIBLE DE LOAD ../private/circus.data")
        return ({})

logging.basicConfig(level=logging.INFO)
client = discord.Client()
data = load_data()
CIRCUS_GUILD_ID = 466950374243303434
REG_CHANNEL_ID = 466961756393046017
MSG_ID = 470682973864329216
FORBIDDEN = "Désolé, seuls les Organisateurs peuvent utiliser cette commande."
MISSING_ARG = "Erreur : Argument manquant"
NOT_FOUND = "Membre non trouvé"
FORCE_REGISTED = "{} a été inscrit de force à l'évenement {} par {}"
FORCE_UNREGISTED = "{} a été désinscrit de force à l'évenement {} par {}"
PRE_REGISTED = "{} a été préinscrit à l'évenement {} par {}"
REREGISTED = "{} s'est fait reregister sur l'évenement {}"
def MENTION(discord_id): return ("<@{}>".format(discord_id))

@client.event
async def on_ready():
    print("Connected (cirque de l'invocateur)")
    await update_msg()
    
@client.event
async def on_message(message):
    if message.guild.id == CIRCUS_GUILD_ID:
        try:
            if message.content.startswith('+'):
                await register(message)
            if message.content.startswith('-'):
                await unregister(message)
            if message.content.startswith('/'):
                av = message.content.split(' ')
                while '' in av : av.remove('')
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
    
def save_data():
    with open("../private/circus.data", 'w') as fd:
        fd.write(json.dumps(data))

with open("../private/token") as fd:
    client.run(json.load(fd))
