import json
import gspread
import random
from oauth2client.service_account import ServiceAccountCredentials

gc = ["https://spreadsheets.google.com/feeds"]
gc = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_name("googlekey.json",gc))
RANDOM_MSG = [
    "Joyeux anniversaire {}",
    "Bon anniversaire {}, woaw tu es vieux maintenant"
]
RANDOM_AGE = [
    "Joyeux anniversaire {pl}, woaw déjà {age} ans ... un pied dans la tombe.",
    "C'est qui qui a {age} ans ? C'EST {pl} ! Joyeux anniversaire !"
]


async def anniv(channel, day, month):
    with open("anniv_serv.save") as fd:
        dic = json.load(fd.read())
    sh = gc.open_by_key(dic[str(channel.guild)])
    cell = sh.cell(day + 2, month + 1).value
    name = cell.split('(')
    age = False
    if len(name) == 2:
        year = name[1].split(')')[0]
        age = year if year > 99 else year + 1900
    name = name[0]
    member = channel.guild.get_member_named(name)
    if age:
        await channel.send(random.choice(RANDOM_AGE).format(pl=member.mention if member else name, age=age))
    else:
        await channel.send(random.choice(RANDOM_MSG).format(member.mention if member else name))
