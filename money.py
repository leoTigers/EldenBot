import discord
import json
import random_message

async def balance(m, args, member):
    you = False if len(args) >= 1 else True
    if not you:
        member = m.guild.get_member_named(" ".join(args))
        if not member:
            return(random_message.not_found(m, msg="``membre non trouvé``"))
    with open("coins.save", 'rw') as fd:
        dic = json.loads(fd)
        if not member.id in dic:
            dic[member.id] = 0
        m.channel.send("{} avez {} coins sur votre compte".format("Vous" if you else member.name, str(dic[member.id])))
        dic.write(json.dumps(dic))
        div.save()
