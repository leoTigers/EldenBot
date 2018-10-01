import json
import discord
from pantheon import pantheon

with open("private/rgapikey") as key:
    panth = pantheon.Pantheon("euw1", key.read(), True)

#verified = {"discordId":"summonerId"}
NOT_VERIFIED = "Vous n'êtes vérifié.\nPour le devenir, connectez vous sur le "\
    + "client League of Legends, puis paramètre > code de vérification tier.\n"\
    + "Entrez votre ID discord ({}) puis cliquez sur valider.\n"\
    + "Entrez ensuite /verif {{votre_nom_d'invocateur}}"
VERIFIED = "Vous êtes vérifié !\nNom d'invocateur : {name}\nSummoner ID : {id}"
BAD_CODE = "Erreur : Le code que vous avez rentrez rentrer ne corespond pas à votre"\
         + " id discord, veuillez résayer. Si le problème persiste, "\
         + "essayez de redémarrer votre client"
ICON_URL = "http://ddragon.canisback.com/latest/img/profileicon/{}.png"

def load_verif():
    with open("data/summoners", 'r') as fd:
        return json.loads(fd.read())

def save_verif(dic):
    with open("data/summoners", 'w') as fd:
        fd.write(json.dumps(dic))

async def verif_all_forum(message, member, args, guild=None):
    count = 0
    members = [member for member in guild.members if "Vérifié" in [
                                            role.name for role in member.roles]
    ]
    verified = load_verif()
    for member in members:
        if str(member.id) not in verified.keys():
            print(member.display_name)
            try:
                summ_data = await panth.getSummonerByName(member.display_name)
            except:
                await message.channel.send("Impossible de vérifier {}".format(member.display_name))
                continue
            verified[str(member.id)] = summ_data['id']
            count += 1
    save_verif(verified)
    await message.channel.send("{} membres ont été ajouté".format(count))

async def verif(message, member, args):
    print(args)
    verified = load_verif()
    if not args:
        if str(member.id) in verified.keys():
            data = await panth.getSummoner(verified[str(member.id)])
            em = discord.Embed(title="Vérification",
                               description=VERIFIED.format(**data)
            )
            em.set_author(name=data['name'], icon_url=ICON_URL.format(data['profileIconId']))
            await message.channel.send(embed=em)
        else:
            await message.channel.send(NOT_VERIFIED.format(member.id))
    else:
        try:
            summ_data = await panth.getSummonerByName(" ".join(args))
        except:
            await message.channel.send("Impossible de trouver l'invocateur")
            return False
        try:
            code = await panth.getThirdPartyCode(summ_data['id'])
            if code != str(member.id):
                raise Exception('bad_code')
        except:
            await message.channel.send(BAD_CODE)
            return False
        verified[str(member.id)] = summ_data['id']
        save_verif(verified)
        await verif(message, member, None)
