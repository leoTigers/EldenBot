from LoupGarou.object import is_alive
import discord

async def update_msg(msg=None, player=None):
        em = discord.Embed(title="Joueur en vie",
                           description="{}\n```Cible 1> {}\nCible 2> {}```".format(
                                '\n'.join(['- ' + i.name for i in game.alive]),
                                *target
                          ))
        em.set_footer(text="Entrez le nom de la cible dans le chat")
        if msg:
            return await msg.edit(embed=em)
        elif player:
            return await player.send(embed=em)

@is_alive("cupidon")
async def cupidon(game, player):
    tagets = (None, None)
    msg= None
    def check(message):
        return message.author == player.member

    for i in range(len(targets))
        while not targets[i] :
            msg = update_msg(msg=msg, player=player)
            inp = await game.client.wait_for('message', check=check)
            target = game.get_player(inp)
            if not target:
                await player.send("Joueur introuvable")
                continue
            if i and target == targets[0]:
                await player.send("Le joueur ne peut pas être amoureux avec lui-même")
                continue
            targets[i] = target
    game.lovers = targets
    await game.announce("amoureux", mp=True, author=targets[0].member,
                  title_args=[str(targets[1])], image=targets[1].member.avatar_url)
    await game.announce("amoureux", mp=True, author=targets[1].member,
                  title_args=[str(targets[0])], image=targets[0].member.avatar_url)
