import discord
from decorator import can_manage_message

MOD_DELETED = ("Votre message a été supprimé par {} pour la raison suivante :"
               + "\n{}\nRappel du message :\n{}")
MOD_MOVE = ("Votre message a été déplacé de {} à {} par {} pour la raison "
            + "suivante :\n{}")

async def move_message(msg, target, reason):
    em = discord.Embed(description=msg.content, timestamp=msg.created_at)
    em.set_footer(text="message déplacé")
    em.set_author(icon_url=msg.author.avatar_url, name=msg.author.name)
    if msg.attachments:
        em.set_image(url=msg.attachments[0].url)
    await target.send(embed=em)
    await msg.delete()
    if reason:
        await msg.author.send(reason)

class CmdModeration:
    @can_manage_message
    async def cmd_mdelete(self, *args, message, channel, member, **_):
        """/mdelete {message_id} [!][*raison]"""
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
    async def cmd_mmove(self, *args, message, member, channel, client, **_):
        """/mmove {message_id} {channel} [!][*raison]"""
        if not args:
            await chanel.send("Pas d'argument reçu")
            return
        msg = await channel.get_message(int(args[0]))
        target = client.get_channel(int(args[1]))
        reason = None
        if len(args) >= 3:
            reason = ' '.join(args[2:])
            if reason.startswith('!'):
                reason = MOD_MOVE.format(channel.mention, target.mention,
                                         member.mention, reason[1:])
        await move_message(msg, target)
        await message.delete()

    @can_manage_message
    async def cmd_mmoveafter(self, *args, channel, member, message, client, **_):
        """/mmoveafter {message_id} {channel} [!][*raison]"""
        if not args:
            await channel.send("Pas d'argument reçu")
            return
        msg = await channel.get_message(int(args[0]))
        target = client.get_channel(int(args[1]))
        reason = None
        if len(args) >= 3:
            reason = ' '.join(args[2:])
            if reason.startswith('!'):
                reason = MOD_MOVE.format(channel.mention, target.mention,
                                         member.mention, reason[1:])
        history = await channel.history(after=msg, limit=None).flatten()
        notified = set()
        for msg in history:
            await move_message(msg, target,
                               reason if msg.author not in notified else None)
            notified.add(msg.author)
