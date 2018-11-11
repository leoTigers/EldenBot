from Eldenbot import client
import discord
import asyncio

class CmdDeleteAllMessage:
    async def deleteallmessage(self, m, member, force, client, *_):
        if not m.author.permissions_in(m.channel).manage_channels and not force:
            await m.channel.send("Tu as pas le droit de faire ça (nécésite la permission : Gérer le canal.)")
            return False
        await m.channel.send(
            "ATTENTION : Tu veux surement pas faire ça !\n" +
            "Toute les données seront perdu à jamais dans mon estomac !\n" +
            "Tape /confirmdelete si tu es VRAIMENT sur. (20 secondes avant expiration)")

        def check_msg(message):
            return (message.content == "/confirmdelete" and message.author == member and message.channel == m.channel)

        try:
            await client.wait_for("message", check=check_msg, timeout=20)
        except:
            await m.channel.send("ECHEC DE CONFIRMATION : veuillez réesayer")
            return None
        await m.channel.purge(limit=10000)
