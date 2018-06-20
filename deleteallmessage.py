import discord
import asyncio

def check_user(message):
    return (message.content == "/confirmdelete")

async def deleteallmessage(m, member, force):
    if not m.author.permissions_in(m.channel).manage_channels and not force:
        await m.channel.send("Tu as pas le droit de faire ça (nécésite la permission : Gérer le canal.)")
        return False
    await m.channel.send(
        "ATTENTION : Tu veux surement pas faire ça !\n" +
        "Toute les données seront perdu à jamais dans mon estomac !" +
        "Tape /confirmdelete si tu es VRAIMENT sur. (20 secondes avant expiration)")
    confirmMessage = await wait_for(message, timeout=20)
    if m.channel != confirmMessage.channel or confirmMessage.author != member:
        await m.channel.send("ECHEC DE CONFIRMATION : veuillez réesayer")
        return None
    await m.channel.purge(limit=10000)
    
