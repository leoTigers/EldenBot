import asyncio
from pantheon import pantheon
from decorator import only_owner

LEAGUE_SCORE = {"BRONZE":0, "SILVER":500, "GOLD":1000, "PLATINUM":1500,
                "DIAMOND":2000, "MASTER":2500, "CHALLENGER":2500}
DIV_SCORE = {"V":0,"IV":100,"III":200,"II":300,"I":400}
QUEUE = {"RANKED_FLEX_SR":"FlexQ", "RANKED_SOLO_5x5":"SoloQ", "RANKED_FLEX_TT":"3v3 "}
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

async def get_ranked_score(summoner_id):
    data = await panth.getLeaguePosition(summoner_id)
    pos = {QUEUE(i["queueType"]): LEAGUE_SCORE(i['tier']) + DIV_SCORE(i['rank'])
            + i['leaguePoints'] for i in data}
    return pos

class CmdLolScore:
    @only_owner
    async def cmd_refreshallscore(self, message):
        verif = load_verif()
        dic = {i:get_ranked_score(i) for i in verif.values()}
        save_score(dic)
