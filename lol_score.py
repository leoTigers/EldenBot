
import discord
import json
import asyncio
from pantheon import pantheon
from decorator import only_owner

LEAGUE_SCORE = {"BRONZE":0, "SILVER":500, "GOLD":1000, "PLATINUM":1500,
                "DIAMOND":2000, "MASTER":2500, "CHALLENGER":2500}
DIV_SCORE = {"V":0,"IV":100,"III":200,"II":300,"I":400}
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

async def get_leaderboard(message, summ_id, rank):
    scores = load_score()
    if str(summ_id) not in scores.keys():
        return None
    verif = load_verif()
    guild = message.guild
    if not guild:
        await message.channel.send("Impoissble de récupérer le classement du serveur")
        return None
    guildv = [verif[member.id] for member in guild.members if member.id in verif.keys()]
    l = [(player, score[player][0][rank]) for player, score in scores if player in guildv]
    l = sorted(l, key=lambda x: x[1])
    return (l.index(summ_id), len(l))

async def get_ranked_score(summoner_id):
    print("getting score for : {}".format(summoner_id))
    data = await panth.getLeaguePosition(summoner_id)
    pos = {QUEUE[i["queueType"]]:
            (LEAGUE_SCORE[i['tier']] + DIV_SCORE[i['rank']] + i['leaguePoints'],
             "{tier} {rank} {leaguePoints} LP".format(**i)) for i in data}
    return pos

class CmdLolScore:
    @only_owner
    async def cmd_refreshallscore(self, message, *_):
        msg = await message.channel.send("Calcul des scores")
        verif = load_verif()
        dic = {i:await get_ranked_score(i) for i in verif.values()}
        save_score(dic)
        msg.edit("{} scores ont été mis à jour".format(dic))

    async def cmd_info(self, message, args, member, *_):
        summ_id, name = None, None
        if not args:
            verif = load_verif()
            if member.id in verif:
                summ_id = verif[member.id]
            else:
                name = member.display_name
        else:
            name = " ".join(args)
        if summ_id:
            data = getSummoner(summ_id)
        else:
            data = getSummonerByName(name)
        if not data:
            await message.channel.send("Impossible de trouver l'invocateur")
            return None
        icon = "http://ddragon.canisback.com/latest/img/profileicon/"+str(data['profileIconId'])+".png"
        score = load_score()
        txt = "```"
        for i in ["SoloQ", "FlexQ", "3v3TT"]:
            lead = get_leaderboard(data['id']
            if lead:
                txt += "{}: {:<12} {}/{}".format(i, score[summ_id][1], *lead))
        colour = 0xDDDDDD
        if summ_id:
            colour = member.colour
        elif message.guild:
            target = message.guild.get_member_named(name)
            if taget : colour = target.colour
        em = discord.Embed(title="Information de l'invocateur", description=txt + "```", colour=member.colour)
        em.set_author(name=data['name'], icon_url=icon)
        await message.channel.send(embed=em)
