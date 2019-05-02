import discord
import random

class CmdUseless:
    async def cmd_thanossnap(self, channel, guild, **_):
        vanished, survivors = [], []
        for user in guild.members:
            if random.randint(0, 1):
                vanished.append(user.name)
            else:
                survivors.append(user.name)
        em = discord.Embed(title="Thanos snap simulator", colour=0xF7AD43)
        em.add_field(name="the vanished", value='\n'.join(vanished))
        em.add_field(name="the survivors", value='\n'.join(survivors))
        await channel.send(embed=em)
