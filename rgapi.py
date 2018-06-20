from pantheon import pantheon
import requests
import asyncio
import discord

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
        return (data["accountId"], data["id"], data["profileIconId"])
    except:
        return (None, None, None)
    
async def getSoloQSeasonMatches(accountId):
    soloQ =  await panth.getMatchlist(accountId, params={"queue":420,"season":11})
    matchlist = soloQ['matches']
    #flexQ = await panth.getMatchlist(accountId, params={"queue":440,"season":11})
    #matchlist += flexQ['matches']
    tasks =  [panth.getMatch(match["gameId"]) for match in matchlist]
    return await asyncio.gather(*tasks)

async def getSeasonMatches(accountId, timeline=False):
    matches =  await panth.getMatchlist(accountId, params={"season":11})
    matchlist = matches['matches']
    tasks = [panth.getMatch(match["gameId"]) for match in matchlist]
    if timeline:
        timelines = [panth.getTimeline(match["gameId"]) for match in matchlist]
        allMatches  = await asyncio.gather(*tasks)
        allTimeline = await asyncio.gather(*timelines)
        return (allMatches, allTimeline)
    return await asyncio.gather(*tasks)




async def getsummid(m, args):
    accountId, summonerId, a = await getSummoner(" ".join(args))
    await m.channel.send("summonerId : {}\naccountId : {}".format(
        str(summonerId),str(accountId)
    ))


async def get_bonus(summonerId, win, totalMatches):
    bonus = {}
    winrate = round((win / totalMatches) * 100)
    mastery = await panth.getChampionMasteries(summonerId)
    mastery7 = [i["championId"] for i in mastery if i["championLevel"] == 7]
    if winrate >= 60 : bonus["High Winrate ({}%)".format(str(winrate))] = 1
    if winrate <= 40 : bonus["Low Winrate ({}%)".format(str(winrate))] = -1
    if 157 in mastery7 : bonus["Yasuo masteries 7"]  = 1
    if 40  in mastery7 : bonus["Janna masteries 7"]  = -0.5
    if 16  in mastery7 : bonus["Soraka masteries 7"] = -0.5
    if 267 in mastery7 : bonus["Nami masteries 7"] = -0.5
    if 117 in mastery7 : bonus["Lulu masteries 7"] = -0.5
    return (bonus)

async def kikimeter(m, args, member):
    if not args: summonerName = member.name
    else : summonerName = "".join(args)
    accountId, summonerId, iconId = await getSummoner(summonerName)
    if not accountId or not summonerId:
        await m.channel.send("Invocateur : {} non trouvé".format(summonerName))
        return None
    league = await getLeagueSoloQ(summonerId)
    if not league:
        await m.channel.send("Cet invocateur n'est pas classé en SoloQ (et il y a que ça qui compte)")
        return None
    msg = await m.channel.send("Récupération des données en cours ...")
    dic1 = {"BRONZE":1,"SILVER":1.5,"GOLD":2.2,"PLATINUM":3,"DIAMOND":4,"MASTER":4.5,"CHALLENGER":5.5}
    dic2 = {"V":0.0, "IV":0.1, "III":0.3, "II":0.4, "I":0.5}
    league_bonus = dic1[league['tier']] + dic2[league['rank']]
    seasonMatches = await getSoloQSeasonMatches(accountId)
    kills, deaths, assists, damage, duration, win = 0, 0, 0, 0, 0, 0
    for match in seasonMatches:
        id = get_player_id(match["participantIdentities"], accountId)
        stat = match["participants"][id - 1]["stats"]
        kills += stat["kills"] 
        deaths += stat["deaths"]
        assists += stat["assists"]
        damage += stat["totalDamageDealt"]
        duration += match["gameDuration"]
        win += stat["win"]
    bonus = await get_bonus(summonerId, win, len(seasonMatches))
    total_bonus = sum(bonus.values())
    if not deaths: deaths = 0.75
    kda = round((kills + assists * 0.75) / deaths, 2)
    dps = round(damage / duration, 2)
    epenis = round(((kills + assists * 0.75) / deaths + damage / duration / 40) * league_bonus + total_bonus * (league_bonus / 2), 2)
    average_kda = [str(round(i / len(seasonMatches), 1)) for i in [kills, deaths, assists]]
    title = "{} possède un e-penis de {} cm\n".format(summonerName, epenis)
    recap =  "__Recap des points__:\n"
    recap += "KDA ({}) : **{}**\n".format("/".join(average_kda), str(kda))
    recap += "DPS ({}) : **{}**\n".format(dps, round(damage / duration / 40, 2))
    recap += "Multiplicateur ({} {}) : **x{}**\n".format(league['tier'].capitalize(), league['rank'], league_bonus)
    if bonus : recap += "BONUS / MALUS : ```diff"
    for i, j in bonus.items():
        recap += "\n{} {} : {}".format("-" if j < 0 else "+", i, str(j))
    if bonus : recap += "```"
    try : colour = m.guild.get_member_named(summonerName).colour
    except : colour = 0xC0C0C0
    em = discord.Embed(title=title, description=recap, colour = colour)
    em.set_footer(text="INFO : " + str(len(seasonMatches)) + " matchs analysés")
    em.set_author(name=summonerName, icon_url="http://ddragon.canisback.com/latest/img/profileicon/"+str(iconId)+".png")
    await msg.edit(content=".",embed=em)

async def afkmeter(m, args, member):
    count = {}
    if not args: summonerName = member.name
    else : summonerName = "".join(argns)
    accountId, summonerId, iconId = await getSummoner(summonerName)
    if not accountId :
        await m.channel.send("Invocateur non trouvé : {}".format(summonerName))
        return None
    try : colour = m.guild.get_member_named(summonerName).colour
    except : colour = 0xC0C0C0
    icon = "http://ddragon.canisback.com/latest/img/profileicon/"+str(iconId)+".png"
    msg = await m.channel.send(embed=discord.Embed(title="Afk Meter",colour=colour).set_author(name=summonerName, icon_url=icon))
    matches, timelines = await getSeasonMatches(accountId, timeline=True)
    for i in range(len(matches)):
        for participant in matches[i]["participantIdentities"]:
            if str(participant["player"]["accountId"]) == str(accountId) :
                id = str(participant["participantId"])
        oldpos,afk = "None",0
        for frame in timelines[i]["frames"]:
            try : j = frame["participantFrames"][str(id)]["position"]
            except : j = {"x":"None","y":"None"}
            pos = str(j["x"])+","+str(j["y"])
            if pos == oldpos :
                afk += 1
                if afk >= 2:
                    print(str(matches[i]["gameId"]))
                    try: count[str(matches[i]["gameId"])] += 1
                    except: count[str(matches[i]["gameId"])] = 2
            else: afk = 0
            oldpos = pos
    txt, nb, mt = "", 0, 0
    for x,y in count.items():
        txt += "\ngame n°" + str(x) +" : **" + str(y) +"** minute(s)"
        nb += 1
        mt += y
    print("Sur les " +str(len(matches)) +" dernières parties\n" +summonerName +" a AFK **" +str(nb) +"** games pour un total de **" +str(mt) +"** minutes\n\n" +txt)
    em = discord.Embed(title="Afk Meter :",description="Sur les " +str(len(matches)) +" dernières parties\n" +summonerName +" a AFK **" +str(nb) +"** games pour un total de **" +str(mt) +"** minutes\n\n" +txt,colour=colour)
    await msg.edit(embed=em.set_author(name=summonerName, icon_url=icon))
