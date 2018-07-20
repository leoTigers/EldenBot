import json
import discord
from random_message import *

def load_link_file():
    try:
        with open("private/link.data", 'r') as fd:
            return (json.loads(fd.read()))
    except:
        print("IMPOSSBILE DE LOAD LE FICHIER private/link.data !")
        return ({})
    
def save_link_file(data):
    with open("private/link.data", 'w') as fd:
        fd.write(json.dumps(data))

linked = load_link_file() #format = {channel_id : [channel_id, ...], ...}

async def show(message):
    txt = "Salons liés:\n"
    for c, l in linked.items():
        if l: txt += "<#{}> -> {}\n".format(c, ", ".join(["<#{}>".format(i) for i in l]))
    await message.channel.send(txt)
    
async def add(message, args):
    channel_id = int(args[1])
    if channel_id not in linked.keys():
        linked[str(channel_id)] = []
    linked[str(channel_id)].append(message.channel.id)
    if len(args) <= 2 or args[2] != "uni": 
        if message.channel.id not in linked.keys():
            linked[str(message.channel.id)] = []
        linked[str(message.channel.id)].append(channel_id)
    save_link_file(linked)

async def delete(message, args):
    deleted = []
    if len(args) == 1:
        for i in linked[str(message.channel.id)]:
            try:
                linked[str(i)].remove(message.channel.id)
                deleted.append((i, message.channel.id))
                if not linked[str(i)]: del linked[str(i)]
            except:
                pass
        await message.channel.send("Link détruit : {}".format(
            "\n".join(["<#{}> -> <#{}>".format(i, j) for i,j in deleted] +
                      ["<#{}> -> <#{}>".format(
                          message.channel.id, i) for i in linked[str(message.channel.id)]])))
        del linked[str(message.channel.id)]
    else:
        try:
            linked[str(message.channel.id)].remove(int(args[1]))
            await message.channel.send("<#{}> -> <#{}>".format(message.channel.id, args[1]))
        except:
            pass
        try:
            linked[args[1]].remove(message.channel.id)
            await message.channel.send("<#{}> -> <#{}>".format(args[1], message.channel.id))
        except:
            pass
        await message.channel.send("")
    save_link_file(linked)

async def link(message, member, args):
    if member.id != 384274248799223818:
        await(forbidden(message))
    else:
        if args[0] == "show"  : await show(message)
        if args[0] == "add"   : await add(message, args)
        if args[0] == "delete": await delete(message, args)

async def send_to_linked(client, message):
    if str(message.channel.id) in linked.keys() and message.author != client.user:
        em = discord.Embed(description=message.content,
                           colour=message.author.colour,
                           timestamp=message.created_at
        )
        try:
            if message.attachments:
                em.set_image(url=message.attachments[0])
        except:
            pass
        em.set_author(name=message.author.name,
                      icon_url=message.author.avatar_url,
                      url=message.jump_url
        )
        em.set_footer(icon_url=message.guild.icon_url,
                      text= message.guild.name + " | #" +
                      message.channel.name)
        for channel in linked[str(message.channel.id)]:
            try: await client.get_channel(channel).send(None,embed=em,)
            except : pass
