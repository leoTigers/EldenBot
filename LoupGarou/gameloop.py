from LoupGarou.Turn.cupidon import cupidon
from LoupGarou.Turn.seer import seer
from LoupGarou.Turn.werewolf import werewolf
from LoupGarou.Turn.witch import witch
from LoupGarou.Turn.village import village


async def game_loop(game):
    day = 1
    game.add_history("Début du jour 1")
    await cupidon(game)
    while not await game_ended(game):
        await seer(game)
        await werewolf(game)
        await witch(game)
        await kill_target(game, reason="loup-garou")
        if await game_ended(game): return
        await village(game)
        await kill_target(game, reason="village")
        if await game_ended(game): return
        day += 1
        game.add_history("Début du jour {}".format(day))

async def game_ended(game):
    if not game.alive:
        return victory(game, "none")
    if game.lovers and len(game.alive) == 2:
        return victory(game, "lovers")
    if not [i for i in game.alive if str(i.role) == "loup-garou"]:
        return victory(game, "villager")
    if not [i for i in game.alive if str(i.role) != "loup-garou"]:
        return victory(game, "loup-garou")
    return False

async def kill_target(game, reason="none"):
    if game.target:
        await game.target.kill(reason=reason)
        if reason == "loup-garou":
            game.add_history("f{game.target} a été tué par les loup-garous")
        game.target = None

async def victory(game, who):
    winner = game.alive
    death_winner = []
    await game.announce("victory_" + who)