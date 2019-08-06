import json
from util.decorator import can_manage_role
from util.exception import InvalidArgs

with open('data/openrole') as fd:
    openrole = json.load(fd)

def save_openrole(dic):
    with open('data/openrole') as fd:
        json.dump(dic, fd)

def find_role_named(guild, name):
    for i in guild.roles:
        if i.name.lower() == role:
            return i
    raise Error("Role non trouvé dans la liste ... :/")
        
class CmdOpenRole:
    @can_manage_role
    def cmd_roleadd(self, *args, channel, guild, **_):
        """/roleadd {role}"""
        global openrole
        if not args:
            raise InvalidArgs("Aucun argument envoyé")
        role = find_role_named(guild, ' '.join(args).lower())
        if str(guild.id) not in openrole:
            openrole[str(guild.id)] = []
        if role.id in openrole[str(guild.id)]:
            raise Error("Role déjà dans la liste, mon papa dit que vous êtes un \"user\"")
        openrole[str(guild.id)].append(role.id)
        save_openrole(openrole)
        await channel.send("Role ajouté")

    @can_manage_role
    def cmd_roledel(self, *args, channel, guild, **_):
        """/roledel {role}"""
        global openrole
        if not args:
            raise InvalidArgs("Aucun argument envoyé")
        role = find_role_named(guild, ' '.join(args).lower())
        if role.id in openrole[str(guild.id)]:
            raise Error("Le Role n'est pas dans la liste, hop là, travail vite fait !")
        openrole[str(guild.id)].remove(role.id)
        save_openrole(openrole)
        await channel.send("Role supprimé")

    def cmd_rolelist(self, *args, guild, channel):
        if str(guild.id) not in openrole:
            await channel.send("Aucun role ouvert")
            return False
        try:
            if args and 'debug' in args[0] or 'id' in args[0]:
                await channel.send('{} ({})'.format(i.name, i.id) for i in guild.roles if i.id in openrole)
            else:
                await channel.send('{}'.format(i.name) for i in guild.roles if i.id in openrole)
        except:
            raise Error("Erreur dans le listing des roles, essayez de lancer un /roleclean")
        
