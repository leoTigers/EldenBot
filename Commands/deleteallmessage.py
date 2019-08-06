class CmdDeleteAllMessage:
    async def cmd_mdeleteallmessage(self, member, channel, force, client, **_):
        if not member.permissions_in(channel).manage_channels and not force:
            await channel.send("Tu as pas le droit de faire ça (nécésite la permission : Gérer le canal.)")
            return False
        await channel.send(
            "ATTENTION : Tu veux surement pas faire ça !\n" +
            "Toute les données seront perdu à jamais dans mon estomac !\n" +
            "Tape /confirmdelete si tu es VRAIMENT sur. (20 secondes avant expiration)")

        check = lambda msg: msg.content == "/confirmdelete" and msg.author == member and msg.channel == channel
        if not force:
            try:
                await client.wait_for("message", check=check, timeout=20)
            except:
                await channel.send("ECHEC DE CONFIRMATION : veuillez réesayer")
                return None
        await channel.purge(limit=10000)
