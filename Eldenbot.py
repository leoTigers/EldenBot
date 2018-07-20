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

from function import *
from roll import roll,bloodlust_roll
from random_message import *
from latex import latex
from money import balance
from rgapi import afkmeter, kikimeter, getsummid
from link import link, send_to_linked
from deleteallmessage import deleteallmessage
#from verif_lol_account import verif


logging.basicConfig(level=logging.INFO)
client = discord.Client()
#wb = gspread.authorize("token_google").open_by_key('1v-MzfsOmmCQNwWFHl86UVrf3lIm5QPitRiJeA4ISIPw')
#wb = wb.get_worksheet(0)

@client.event
async def on_ready():
    serv = client.get_guild(419539636147453953)
    
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
            await command(m, member, cmd, args, force)
        except Exception:
            em = discord.Embed(title="Oh no !  😱",
                               description="Une erreur s'est produite lors de l'éxécution de la commande\n" + msg("- [FATAL ERROR]\n" + traceback.format_exc()),
                               colour=0xFF0000).set_footer(text="command : " + m.content,icon_url=m.author.avatar_url)
            await m.channel.send(embed=em)
    if client.user in m.mentions and m.author != client.user:
        await random_message(client, m)
    await send_to_linked(client, m)


async def command(m, member, cmd, args, force):
    if cmd == "r" or cmd == "roll" : await roll(m, args)
    elif cmd == "rb" or cmd == "br": await bloodlust_roll(m, args)
    elif cmd == "latex" : await latex(m, args)
    elif cmd == "bash" : await bash(m, member, args)
    elif cmd == "python" : await python(m, member, args)
    elif cmd == "money" : await balance(m ,args, member)
    elif cmd == "getsummid" : await getsummid(m, args)
    elif cmd == "kikimeter" : await kikimeter(m, args, member)
    elif cmd == "afkmeter" : await afkmeter(m, args, member)
    elif cmd == "deleteallmessage" : await deleteallmessage(client, m, member, force)
    elif cmd == "link" : await link(m, member, args)

async def python(m, member, args):
    if member.id != 384274248799223818:
        await(forbidden(m))
    else:
        await m.channel.send(eval(" ".join(args)))
    
async def bash(m, member, args):
    if member.id != 384274248799223818:
        await(forbidden(m))
    else:
        rt = subprocess.run(shlex.split(" ".join(args)),timeout=10, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        await m.channel.send(msg(rt.stdout.decode("utf-8")))


fd = open("private/token")
client.run(json.load(fd))
fd.close()
