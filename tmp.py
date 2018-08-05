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

txt = """460: Lawrento
206: Mıthrandır
181: Lybal
136: imaxaroth
134: Goldorgh
125: RFM Varlane
122: Guillorc
 97: darroll
 78: Kyunsei
 75: AureIion SouI
 75: ShadesSlayer
 74: Shamsiel
 70: Moumix
 66: Le Nécromancien
 63: TehKsy
 59: Erwan
 54: DearPear
 53: Eiael
 49: Kerbiboul
 49: SHAars
 48: khromer
 45: LadyStegosaurus
 45: Andyspak
 44: zerhel
 43: Kyotiste Senpai
 39: I Thrash I
 38: Lutcha
 37: Gabriel Angelos
 37: reformed Wistorm
 36: Cypher
 36: Llaÿth
 36: How 2 Ahri
 33: Hyôka
 31: Inferno Cop
 31: Leo tigers
 30: Leecoste
 28: NectazuOppai
 26: SkithirX Nurgle
 26: Max Nobody
 23: ßläckMäster
 22: Hiyoko42
 21: CELUI QUI CRIE
 20: Sweety Orka
 19: Mithrognon
 19: LordStegosaurus
 19: Cαmille
 18: AliasTcherki
 17: Dragon Magistral
 16: Princess Asuna
 13: Matou97
 12: Firkraag
 12: Sweet Neat
 12: Héraklia
 12: nophinx
 12: La Teknomobile
 11: Sacomano
 11: DJ Bipomme
 10: DYNAMITE BODY
 10: Tout4nkharton
 10: Vrafal
 10: Gemmelekiwi
 10: Lybal Alyborias
  9: Liggom
  9: Salsify
  9: Creepy Pumpkins
  9: Throsheld
  9: I Ðeath Mark you
  8: Arhkeid
  8: ArLongBE
  8: Tapehmwadsu
  8: Tranme
  8: The Vermintide
  7: Myrdhin Dale
  7: iKazor 
  7: DutchWolf
  7: Vierge Farouche
  7: evanescence29
  7: Raccoon Bot
  7: Superbilly
  6: Soka
  6: SukiHeaven
  6: SID3
  6: Loutre Mystique
  6: Kuri
  5: PahnetSeksom
  5: Legend of KaiSa
  5: DragonDarkNess17
  5: NotJustAHammer
  5: Un Jo Poisson
  5: Ai Se Eu Te Pego
  5: The Wind Exiled
  5: iorektum
  5: PSJJJJ
  5: MyOwnWings
  5: NeverTroll33
  5: invisible tueur"""

logging.basicConfig(level=logging.INFO)
client = discord.Client()

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
            await command(m, member, cmd, args, force)
        except Exception:
            em = discord.Embed(title="Oh no !  😱",
                               description="Une erreur s'est produite lors de l'éxécution de la commande\n" + "- [FATAL ERROR]\n" + traceback.format_exc(),
                               colour=0xFF0000).set_footer(text="command : " + m.content,icon_url=m.author.avatar_url)
            await m.channel.send(embed=em)


async def command(m, member, cmd, args, force):
    if cmd == "test" :
        try: colour = member.colour
        except : colour = 0x000000
        line = txt.split('\n')
        em = discord.Embed(title="Invocateurs rencontrés les 365 derniers jours",
                           description="```" + "\n".join(line) + "```",
                           colour=colour)
        mid = len(line) // 2 + len(line) % 2
        await m.channel.send(".", embed=em)

fd = open("private/token")
client.run(json.load(fd))
fd.close()
