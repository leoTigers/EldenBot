from pantheon import pantheon
import requests
import asyncio
import discord
import time

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

async def getLastYearHistory(accountId):
    index = 0
    tasks = []
    begin = int(time.time()) * 1000 - 31536000000
    print(begin)
    while True:
        matchs = await panth.getMatchlist(accountId, params={"beginIndex":index, "beginTime":begin})
        tasks += [panth.getMatch(match["gameId"]) for match in matchs['matches']]
        index += 100
        if matchs["endIndex"] != index: break
    return await asyncio.gather(*tasks)
    
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


async def premade(message, args, member):
    if not args : summonerName = member.name
    else : summonerName = " ".join(args)
    accountId, summonerId, iconId = await getSummoner(summonerName)
    result = {}
    msg = await message.channel.send("Récupération de l'historique")
    matchs = await getLastYearHistory(accountId)
    await msg.edit(content="Analyse des matchs")
    for match in matchs:
        for player in [i["player"]["summonerId"] for i in match["participantIdentities"]
                       if "summonerId" in i["player"].keys()
                       and i["player"]["summonerId"] != summonerId]:
            if player in result.keys(): result[player] += 1
            else : result[player] = 1
    await msg.edit(content="Tri des données")
    result = {player : nb for player, nb in result.items() if nb >= 5}
    r = sorted(result.items(), key=lambda x: x[1])[::-1]
    await msg.edit(content="Récupération des noms d'invocateur")
    tasks = [panth.getSummoner(summonerId) for summonerId, nb in r]
    response = await asyncio.gather(*tasks)
    txt = "```{}```".format(
        "\n".join(["{:>3}: {}".format(r[i][1], response[i]['name']) for i in range(len(r))]))
    if len(txt) >= 2000 : txt = txt[:1996] + "```"
    em = discord.Embed(title="Invocateurs rencontrés les 365 derniers jours",
                       description=txt)
    em.set_author(name=summonerName,
                  icon_url="http://ddragon.canisback.com/latest/img/profileicon/"+str(iconId)+".png")
    await msg.edit(content="done", embed=em)
    

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
    else : summonerName = "".join(args)
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
    em = discord.Embed(title="Afk Meter :",description="Sur les " +str(len(matches)) +" dernières parties\n" +summonerName +" a AFK **" +str(nb) +"** games pour un total de **" +str(mt) +"** minutes\n\n" +txt,colour=colour)
    await msg.edit(embed=em.set_author(name=summonerName, icon_url=icon))