import discord
import json
import asyncio
from pantheon import pantheon
from decorator import only_owner

LEAGUE_SCORE = {"IRON": 0, "BRONZE":500, "SILVER":1000, "GOLD":1500, "PLATINUM":2000,
                "DIAMOND":2500, "MASTER":2600, "GRANDMASTER": 2600, "CHALLENGER":2600}
DIV_SCORE = {"IV":0,"III":110,"II":220,"I":330}
QUEUE = {"RANKED_FLEX_SR":"FlexQ", "RANKED_SOLO_5x5":"SoloQ", "RANKED_FLEX_TT":"3v3TT"}
with open("private/rgapikey") as key:
    panth = pantheon.Pantheon("euw1", key.read(), True)

def load_verif():
    with open("data/summoners", 'r') as fd:
        return json.loads(fd.read())

def load_score():
    with open("data/rank_score", 'r') as fd:
        return json.loads(fd.read())

def save_score(dic):
    with open("data/rank_score", 'w') as fd:
        fd.write(json.dumps(dic))

async def get_leader(message, rank):
    scores = load_score()
    verif = load_verif()
    guild = message.guild
    if not guild:
        await message.channel.send("Impoissble de récupérer le classement du serveur")
        return None
    guildv = [str(verif[str(member.id)]) for member in guild.members if str(member.id) in verif.keys()]
    l = [(player, score[rank]) for player, score in scores.items()
            if player in guildv and rank in score.keys()]
    l = sorted(l, key=lambda x: x[1][0])[::-1]
    return l

async def get_leaderboard_place(message, summ_id, rank):
    summ_id = str(summ_id)
    scores = load_score()
    if summ_id not in scores.keys():
        return None
    if rank not in scores[summ_id].keys():
        return None
    verif = load_verif()
    guild = message.guild
    if not guild:
        await message.channel.send("Impoissble de récupérer le classement du serveur")
        return None
    guildv = [str(verif[str(member.id)]) for member in guild.members if str(member.id) in verif.keys()]
    l = [(player, score[rank][0]) for player, score in scores.items()
            if player in guildv and rank in score.keys()]
    l = sorted(l, key=lambda x: x[1])[::-1]
    return ([i[0] for i in l].index(summ_id) + 1, len(l))

async def get_ranked_score(summoner_id):
    print("getting score for : {}".format(summoner_id))
    data = await panth.getLeaguePosition(summoner_id)
    pos = {QUEUE[i["queueType"]]:
            (LEAGUE_SCORE[i['tier']] + DIV_SCORE[i['rank']] + i['leaguePoints'],
             "{:>8} {rank:<3} {leaguePoints:^3}LP".format(i['tier'].capitalize(), **i))
           for i in data}
    return pos

class CmdLolScore:
    @only_owner
    async def cmd_refreshallscore(self, *args, message, **_):
        msg = await message.channel.send("Calcul des scores")
        verif = load_verif()
        dic = {i:await get_ranked_score(i) for i in verif.values()}
        save_score(dic)
        await msg.edit(content="{} scores ont été mis à jour".format(len(dic)))

    async def cmd_ladder(self, *args, message, **_):
        if not args or args[0] not in ['SoloQ', 'FlexQ', '3v3TT']:
            await message.channel.send("Préciser la queue [SoloQ/FlexQ/3v3TT]")
            return
        lst = await get_leader(message, args[0])
        lst = lst[:20]
        tasks = [panth.getSummoner(summ_id) for summ_id in [i[0] for i in lst]]
        summ_name = [i['name'] for i in await asyncio.gather(*tasks)]
        txt = "```{}```".format('\n'.join(["{:>2}.{:>15} {}".format(i+1, summ_name[i], j[1][1])
                                for i,j in enumerate(lst)]))
        await message.channel.send(txt)

    async def cmd_info(self, *args, message, member, **_):
        summ_id, name = None, None
        if not args:
            verif = load_verif()
            if member.id in verif:
                summ_id = verif[str(member.id)]
            else:
                name = member.display_name
        else:
            name = " ".join(args)
        if summ_id:
            data = await panth.getSummoner(summ_id)
        else:
            data = await panth.getSummonerByName(name)
        if not data:
            await message.channel.send("Impossible de trouver l'invocateur")
            return None
        icon = "http://ddragon.canisback.com/latest/img/profileicon/"+str(data['profileIconId'])+".png"
        score = load_score()
        txt = ""
        for i in ["SoloQ", "FlexQ", "3v3TT"]:
            lead = await get_leaderboard_place(message, data['id'], i)
            if lead:
                txt += "``{}: {} {:>2}/{}``\n".format(i, score[str(data['id'])][i][1], *lead)
        colour = 0xDDDDDD
        if summ_id:
            colour = member.colour
        elif message.guild:
            target = message.guild.get_member_named(name)
            if target : colour = target.colour
        em = discord.Embed(title="Information de l'invocateur", description=txt + "", colour=member.colour)
        em.set_author(name=data['name'], icon_url=icon)
        await message.channel.send(embed=em)
