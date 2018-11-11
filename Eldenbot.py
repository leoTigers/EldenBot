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

if __name__ == '__main__':
    from function import *
    from random_message import *
    from roll import CmdRoll
    from latex import CmdLatex
    #from money import balance
    from rgapi import CmdRgapi
    from link import CmdLink, send_to_linked
    from deleteallmessage import CmdDeleteAllMessage
    from verif import CmdVerif
    from lol_score import CmdLolScore
    from music import CmdMusic
    from moderation_tools import CmdModeration

    class Command(CmdRoll, CmdLatex, CmdRgapi, CmdLink, CmdDeleteAllMessage,
                  CmdVerif, CmdLolScore, CmdMusic, CmdModeration):
        async def cmd_help(self, message, *_):
            with open("help", 'r') as fd:
                await message.channel.send(fd.read())
        async def python(self, m, args, member, *_, asyncrone=False):
            if member.id != 384274248799223818:
                await(forbidden(m))
            else:
                if asyncrone:
                    rt = await eval(" ".join(args))
                else:
                    rt = eval(" ".join(args))
                await m.channel.send(rt)
        async def cmd_python(self, *args) : await self.python(*args, asyncrone=False)
        async def cmd_apyhton(self, *args) : await self.python(*args, asyncrone=True)
    command = Command()

logging.basicConfig(level=logging.INFO)
client = discord.Client()

#wb = gspread.authorize("token_google").open_by_key('1v-MzfsOmmCQNwWFHl86UVrf3lIm5QPitRiJeA4ISIPw')
#wb = wb.get_worksheet(0)

@client.event
async def on_ready():
    print("Connected")

@client.event
async def on_message(m):
    if m.content.startswith('/') :#and m.author == client.user:
        member = m.author
        cmd = m.content.split(" ")[0][1:].lower()
        force = True if cmd == "force" and member.id == 384274248799223818 else False
        if force:
            cmd = m.content.split(" ")[1]
            args = m.content.split(" ")[2:]
        else: args = m.content.split(" ")[1:]
        try:
            function = getattr(command, "cmd_" + cmd)
        except:
            return
        try:
            await function(m, args, member, force, client)
        except Exception:
            em = discord.Embed(title="Oh no !  😱",
                               description="Une erreur s'est produite lors de l'éxécution de la commande\n" + msg("- [FATAL ERROR]\n" + traceback.format_exc()),
                               colour=0xFF0000).set_footer(text="command : " + m.content,icon_url=m.author.avatar_url)
            await m.channel.send(embed=em)
    if client.user in m.mentions and m.author != client.user:
        await random_message(client, m)
    await send_to_linked(client, m)


if __name__ == '__main__':
    fd = open("private/token")
    client.run(json.load(fd))
    fd.close()
