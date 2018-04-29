from pantheon import pantheon
import asyncio
import discord

rg = asyncio.get_event_loop()

with open("private/rgapikey") as key:
    panth = pantheon.Pantheon("euw1", key.read(), True)

def get_player_id(pi, accid):
    for i in pi:
        if i["player"]["accountId"] == accid:
            return i["participantId"]
    return None

async def getLeagueSoloQ(summonerId):
    data = await panth.getLeaguePosition(summonerId)
    for league in data:
        if league['queueType'] == 'RANKED_SOLO_5x5':
            return (league)
    return (None)

async def getSummoner(name):
    try:
        data = await panth.getSummonerByName(name)
        return (data["accountId"], data["id"])
    except:
        return (None, None)
    
async def getSoloQSeasonMatches(accountId):
    soloQ =  await panth.getMatchlist(accountId, params={"queue":420,"season":11})
    matchlist = soloQ['matches']
    #flexQ = await panth.getMatchlist(accountId, params={"queue":440,"season":11})
    #matchlist += flexQ['matches']
    tasks =  [panth.getMatch(match["gameId"]) for match in matchlist]
    return await asyncio.gather(*tasks)


async def kikimeter(m, args):
    summonerName = args[0]
    accountId, summonerId = await getSummoner(summonerName)
    if not accountId or not summonerId:
        await m.channel.send("Invocateur : {} non trouvé".format(summonerName))
        return None
    league = await getLeagueSoloQ(summonerId)
    if not league:
        await m.channel.send("Cet invocateur n'est pas classé en SoloQ (et il y a que ça qui compte)")
        return None
    msg = await m.channel.send("Récupération des données en cours ...")
    dic1 = {"BRONZE":1,"SILVER":2,"GOLD":3,"PLATINUM":4,"DIAMOND":5,"MASTER":6.7,"CHALLENGER":9.2}
    dic2 = {"V":0.0, "IV":0.2, "III":0.4, "II":0.6, "I":0.8}
    league_bonus = dic1[league['tier']] + dic2[league['rank']]
    seasonMatches = await getSoloQSeasonMatches(accountId)
    kills, deaths, assists = 0, 0, 0
    bonus = {}
    for match in seasonMatches:
        id = get_player_id(match["participantIdentities"], accountId)
        stat = match["participants"][id - 1]["stats"]
        kills += stat["kills"] 
        deaths += stat["deaths"]
        assists += stat["assists"]
    if not deaths: deaths = 0.75
    kda = round((kills + assists * 0.75) / deaths, 2)
    epenis = round(((kills + assists * 0.75) / deaths) * league_bonus, 2)
    average_kda = [str(round(i / len(seasonMatches), 1)) for i in [kills, deaths, assists]]
    title = "{} possède un e-penis de {} cm\n".format(summonerName, epenis)
    recap =  "__Recap des points__:\n"
    recap += "KDA ({}) : **{}**\n".format("/".join(average_kda), str(kda))
    recap += "Multiplicateur ({} {}) : **x{}**\n".format(league['tier'], league['rank'], league_bonus)
    recap += "BONUS / MALUS : ```diff\n" if bonus else ""
    await msg.edit(content=".",embed=discord.Embed(title=title,
                                                   description=recap).set_footer(text=str(len(seasonMatches)) + " matchs analysés"))
