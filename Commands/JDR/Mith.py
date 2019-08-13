import json
import discord
import gspread
from oauth2client.service_account import ServiceAccountCredentials as sac
from PIL import Image, ImageDraw, ImageFilter
from io import BytesIO, BufferedIOBase
from ..roll import roll

from util.exception import InvalidArgs, NotFound
from util.function import get_member
from util.constant import POUBELLE_ID
from typing import List

credentials = sac.from_json_keyfile_name("private/googlekey.json", ["https://spreadsheets.google.com/feeds"])
gc = gspread.authorize(credentials)

with open("private/mith_sheets.json") as fd:
    CHAR_SHEET = json.load(fd)
MJ_ID = 203934874204241921

SIZE = 128
MIN_Y = 16
MAX_Y = SIZE - 16
MIN_X = SIZE - SIZE // 4
MAX_X = SIZE * 6


BORDER_WIDTH = 8

START_X = MIN_X + BORDER_WIDTH
END_X = MAX_X - BORDER_WIDTH

async def create_image(avatar_url, current_hp, max_hp):
    """

    Args:
        avatar_url (discord.Asset):
        current_hp (int):
        max_hp (int):

    Returns:

    """
    result = Image.new('RGBA', (SIZE * 6, SIZE), (0, 0, 0, 0))
    raw_data = await avatar_url.read()
    raw_avatar = Image.open(BytesIO(raw_data))
    raw_avatar = raw_avatar.resize((SIZE, SIZE), Image.ANTIALIAS)

    bigsize = (raw_avatar.size[0] * 3, raw_avatar.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(raw_avatar.size, Image.ANTIALIAS)
    raw_avatar.putalpha(mask)

    # DRAW HP BAR BORDER

    health_percent = current_hp / max_hp
    if health_percent > 0.5:
        health_color = (0x2e, 0xcc, 0x71, 255) # green
    elif health_percent > 0.2:
        health_color = (0xf1, 0xc4, 0x0f, 255) # gold
    else:
        health_color = (0xe7, 0x4c, 0x3c, 255) # red
    pix = result.load()
    for y in range(MIN_Y, MAX_Y):
        for x in range(MIN_X, MAX_X):
            if x in range(START_X, END_X) and y in range(MIN_Y + BORDER_WIDTH, MAX_Y - BORDER_WIDTH):
                if (x - START_X) / (END_X - START_X) <= health_percent:
                    pix[x, y] = health_color
            else:
                pix[x, y] = (0, 0, 0, 255)



    result.paste(raw_avatar, (0, 0), raw_avatar)
    r = BytesIO()
    result.save(r, format='PNG')
    r.seek(0)
    return r


class CmdJdrMith:
    async def cmd_takedamage(self, *args : List[str], message, member, channel, guild, client, heal=False, **_):
        """
        Args:
            *args (List[str]):
            member (discord.Member):
            channel (discord.Channel):
            guild (discord.Guild):
            client (discord.Client):
            **_:

        Returns:

        """
        if len(args) < 1:
            raise InvalidArgs("Usage: /takedamage [joueur] {domage}")
        if len(args) == 1:
            target = member
        else:
            membername = ' '.join(args[:-(len(args) - 1)])
            target = get_member(guild, membername) # type: discord.Member
            if not target:
                raise NotFound(f"Member named {membername} not found")
        expr = args[-1]
        roll_result = roll(expr)

        damage = roll_result.total
        if damage < 0:
            damage = 0

        elif heal:
            damage = -damage

        wsh = gc.open_by_key(CHAR_SHEET[str(target.id)]).sheet1
        cell_list = wsh.range('C13:C14')
        new_hp = int(cell_list[0].value) - damage
        if new_hp > int(cell_list[1].value):
            new_hp = int(cell_list[1].value)

        em = discord.Embed(colour=target.colour)
        if roll_result.dices:
            em.add_field(name="Lancé de dé", value=f"{member.mention} {roll_result.intro_sentence()}\n{roll_result.format_results()}")
        if damage > 0:
            em.add_field(name="Resultat", value=f"{target.mention} a pris **{damage}** point{'s' if damage > 1 else ''} de dégats.\n"
                         f"Il lui reste **{new_hp}** / {cell_list[1].value}", inline=False)
        else:
                em.add_field(name="Resultat", value=f"{target.mention} a gagné **{-damage}** point{'s' if damage > 1 else ''} de vie.\n"
                f"Il lui reste **{new_hp}** / {cell_list[1].value}", inline=False)
        em.set_author(name=target.name, icon_url=target.avatar_url)
        em.set_footer(text=message.content)
        msg = await channel.send(embed=em)

        img = await create_image(target.avatar_url_as(format="png", size=1024), new_hp, int(cell_list[1].value))

        trash_msg = await client.get_channel(POUBELLE_ID).send(file=discord.File(fp=img, filename="a.png")) #type: discord.Message
        em.set_image(url=trash_msg.attachments[0].url)
        await msg.edit(embed=em)

        cell_list[0].value = new_hp
        wsh.update_cells(cell_list)

    async def cmd_td(self, *args, **kwargs): await self.cmd_takedamage(*args, **kwargs)
    async def cmd_hd(self, *args, **kwargs): await self.cmd_takedamage(*args, **kwargs, heal=True)

    async def cmd_gmroll(self, *args, message, member, client,**_):
        if not args or not args[0]:
            args = "1d100"
        expr = "".join(args)
        r = roll(expr)
        em = discord.Embed(
            title="Lancé de dés",
            description=f"{member.mention} {r.intro_sentence()}\n\n{r.format_results()}\n\nTotal : **{r.total}**",
            colour=member.colour
        ).set_footer(text=message.content).set_author(name=member.name, icon_url=member.avatar_url)
        await message.channel.send(embed=em)
        await client.get_user(203934874204241921).send(embed=em)
        try:
            await message.delete()
        except discord.HTTPException:
            pass

    async def cmd_gr(self, *args, **kwargs): await self.cmd_gmroll(*args, **kwargs)