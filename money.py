import discord
import json
import random_message

def open_dic():
    with open("coins.save", 'r') as fd:
        dic = json.load(fd.read())
    return(dic)

def save_dic(dic):
    with open("coins.save", 'w') as fd:
        fd.write(json.dumps(dic))
    return(None)

def create_user(dic, user):
    dic[user] = {"money" : 0, "daily_countdown" : 0}
    save_dic(dic)

async def balance(m, args, member):
    you = False if len(args) >= 1 else True
    if not you:
        member = m.guild.get_member_named(" ".join(args))
        if not member:
            return(random_message.not_found(m, msg="``membre non trouvé``"))
    dic = open_dic()
    uid = str(member.id)
    if not uid in dic.keys():
        create_user(dic, uid)
    await m.channel.send("{} avez {} coins sur votre compte".format("Vous" if you else member.name, str(dic[uid]["money"])))

async def pay(m, args, member):
    dic = open_dic()
    
    dic[(member.id)]["money"]
    await m.channel.send("Vous avez donnez")
