import discord

MOD_DELETED = ("Votre message a été supprimé par {} pour la raison suivante :"
               + "\n{}\nRappel du message :\n{}")
MOD_MOVE = ("Votre message a été déplacé de {} à {} par {} pour la raison "
            + "suivante :\n{}")

class CmdModeration:
    @can_manage_message
    async def cmd_mdelete(self, message, args, member, *_):
        channel = message.channel
        if not args:
            await channel.send("Pas d'argument reçu")
            return
        msg = await channel.get_message(int(args[0]))
        await msg.delete()
        await message.delete()
        if len(args) >= 2:
            reason = ' '.join(args[1:])
            if reason.startswith('!'):
                await msg.author.send(MOD_DELETED.format(member.mention, reason[1:],
                                                         msg.content))

    @can_manage_message
    async def cmd_mmove(self, message, args, member, force, client, *_):
        channel = message.channel
        if not args:
            await chanel.send("Pas d'argument reçu")
            return
        msg = await channel.get_message(int(args[0]))
        target = client.get_channel(int(args[1]))
        em = discord.Embed(description=msg.content, timestamp=msg.created_at)
        em.set_footer(text="message déplacé par la modération")
        em.set_author(icon_url=msg.author.avatar_url, name=msg.author.name)
        await target.send(embed=em)
        await msg.delete()
        await message.delete()
        if len(args) >= 3:
            reason = ' '.join(args[2:])
            if reason.startswith('!'):
                await msg.author.send(MOD_MOVE.format(channel.mention, target.mention,
                                                      member.mention, reason[1:]))
