#!/usr/bin/python3
import sys
import os
import discord
import asyncio
import logging
import json
import traceback
import shlex
import subprocess

logging.basicConfig(level=logging.INFO)
client = discord.Client()

ROLES = ["jdr", "lol", "créateurs en herbe"]

def get_role(name):
    return []

@client.event
async def on_message(m):
    if m.content.startswith('/get') :#and m.author == client.user:
        m.content = m.content.lower()
        args = ' '.join(m.content.split(' ')[1:])
        if args in ROLES:
            role = [role for role in m.guild.roles if role.name.lower() == args][0]
            await m.author.add_roles(role)
            await m.channel.send("role ajouté")
        else:
            await m.channel.send("role non trouvé dans la liste des roles valides")

if __name__ == '__main__':
    fd = open("private/token")
    client.run(json.load(fd))
    fd.close()
