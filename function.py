import discord

def msg(message, error=False):
    if error : return("```diff\n- [ERREUR]\n{}```".format(message))
    else :     return("```diff\n{}```".format(message))
    
def get_channel_named(server, name):
    return(discord.utils.get(server.channels, name=name))

def get_role_id(server, role_id):
    for i in server.roles:
        if i.id == role_id : return(i)
    return(None)

def get_role_named(server, name):
    for i in server.roles:
        if i.name == name : return(i)
    return(None)
