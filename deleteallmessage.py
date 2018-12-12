from Eldenbot import client
import discord
import asyncio

class CmdDeleteAllMessage:
    async def cmd_mdeleteallmessage(self, m, args, member, force, client, *_):
        if not m.author.permissions_in(m.channel).manage_channels and not force:
            await m.channel.send("Tu as pas le droit de faire ça (nécésite la permission : Gérer le canal.)")
            return False
        await m.channel.send(
            "ATTENTION : Tu veux surement pas faire ça !\n" +
            "Toute les données seront perdu à jamais dans mon estomac !\n" +
            "Tape /confirmdelete si tu es VRAIMENT sur. (20 secondes avant expiration)")

        check = lambda msg: msg.content == "/confirmdelete" and msg.author == member and msg.channel == m.channel
        try:
            await client.wait_for("message", check=check, timeout=20)
        except:
            await m.channel.send("ECHEC DE CONFIRMATION : veuillez réesayer")
            return None
        await m.channel.purge(limit=10000)
