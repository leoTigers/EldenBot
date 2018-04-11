import discord
import json
import random_message

async def balance(m, args, member):
    you = False if len(args) >= 1 else True
    if not you:
        member = m.guild.get_member_named(" ".join(args))
        if not member:
            return(random_message.not_found(m, msg="``membre non trouvé``"))
    with open("coins.save", 'r') as fd:
        dic = json.loads(fd.read())
        print("loaded :", dic)
    uid = str(member.id)
    if not uid in dic.keys():
        dic[uid] = 0
        with open("coins.save", 'w') as fd:
            print("saved :", dic)
            fd.write(json.dumps(dic))
    await m.channel.send("{} avez {} coins sur votre compte".format("Vous" if you else member.name, str(dic[uid])))
