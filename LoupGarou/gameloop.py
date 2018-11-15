

async def game_loop(game):
    await cupidon(game)
    while not await game_ended(game):
        await seer(game)
        await werewolf(game)
        await witch(game)
        await kill_target(game, reason="werewolf")
        await villager(game)
        await kill_target(game, reason="village")

async def game_ended(game):
    if not game.alive:
        return victory("none")
    if game.lovers and len(game.alive) == 2:
        return victory("lovers")
    if not [i for i in game.alive if str(game.role) == "loup-garou"]:
        return victory("villager")
    if not [i for i in game.alive if str(game.role) != "loup-garou"]:
        return victory("werewolf")
    return False
