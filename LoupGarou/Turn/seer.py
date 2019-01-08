import discord

@is_alive("voyante")
async def seer(game, player):
    check = lambda message: message.author == player.member

    em = discord.Embed(title="Joueur en vie",
                       description='\n'.join(
                            ['- ' + i.name for i in game.alive if i != player]
                      ))
    em.set_footer(text="Entrez le nom de la cible dans le chat")
    await player.send(embed=em)
    target = None
    while not target:
        inp = await game.client.wait_for('message', check=check)
        target = game.get_player(inp)
        if not target :
            await player.send("Joueur introuvable")
    await game.announce("voyante_" + target.role.name, mp=True,
                        author=player, image=target.role.image)
