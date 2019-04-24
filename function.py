import discord
import re

mention_regex = re.compile(r"(?<=^<@)\d+(?=>$)")

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

def get_member(guild, name):
    member = guild.get_member_named(name)
    if member:
        return member
    match = re.search(mention_regex, name)
    if match:
        return guild.get_member(int(match[0]))
    if name.isdigit():
        return guild.get_member(int(name))
    return None
