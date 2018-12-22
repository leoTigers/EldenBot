import random
import discord
import asyncio

def roll_dice(nb, face):
    l = []
    for i in range(nb):
        l.append(random.randint(1,face))
    return (l)

class CmdRoll:
    async def cmd_roll(self, *args, m, **_):
        arg = "".join(args).replace(" ","").lower()
        d,f,bonus = 1,100,0
        if 'd' in arg :
            d = int(arg.split('d')[0])
            arg = arg.split('d')[1]
        if '+' in arg :
            bonus = int(arg.split('+')[1])
            arg = arg.split('+')[0]
        if '-' in arg :
            bonus = - int(arg.split('-')[1])
            arg = arg.split('-')[0]
        if arg : f = int(arg)
        r  =roll_dice(d, f)
        v1 = m.author.name
        v2 = " avec un bonus de {}".format(str(bonus)) if bonus else ""
        v3 = ", ".join([str(i) for i in r])
        await m.channel.send(embed=discord.Embed(title="Lancé de dés",description="{} a lancé {} dé {}{} et a obtenu :\n\n**{}**\n\nTotal : **{}**".format(v1,str(d),str(f),v2,v3,str(sum(r) + bonus)),colour=m.author.color).set_author(name=m.author.name,icon_url=m.author.avatar_url))
        try:
            await m.delete()
        except:
            pass

    async def cmd_bloodlustroll(self, *args, m, **_):
        arg = "".join(args).replace(" ","")
        if '+' in arg :
            r = int(arg.split('+')[1])
            d = int(arg.split('+')[0])
        else :
            d = int(arg)
            r = 0
        l = roll_dice(d ,6)
        await m.channel.send(embed=discord.Embed(title="Lancé de dés (Bloodlust)",description="{} a lancé {} dés avec {} risques, il a obtenu :\n\n**{}**\n\nTotal : **{}** (Qualités : **{}**)".format(m.author.name,str(d),str(r),", ".join([str(i) for i in l]),sum(l),str(len([i for i in l if i%2 == 0])+r)),colour=m.author.color).set_author(name=m.author.name,icon_url=m.author.avatar_url))
        try:
            await m.delete()
        except:
            pass

    async def cmd_r(self, *args, **kwargs): await self.cmd_roll(*args, **kwargs)
    async def cmd_br(self, *args, **kwargs): await self.cmd_bloodlustroll(*args, **kwargs)
    async def cmd_rb(self, *args, **kwargs): await self.cmd_bloodlustroll(*args, **kwargs)
