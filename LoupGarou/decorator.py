import logging

logger = logging.getLogger("LG.decorator")

def is_alive(role):
    def deco_wrap(function):
        async def wrapper(game):
            for player in game.alive:
                if player.role == role:
                    if role == "sorcière" and not player.role.poison and not player.role.heal:
                        continue
                    game.add_history(f"Début du tour de '{role}' ({player})", show=False)
                    try:
                        await game.announce("urturn_" + role, author=player.member,
                                            mp=True, image=player.role.image)
                    except KeyError:
                        game.logger.error(f"Key Error on uturn_{role}")
                    await function(game, player)
        return wrapper
    return deco_wrap

def are_alive(role):
    def deco_wrap(function):
        async def wrapper(game):
            player_list = []
            for player in game.alive:
                if player.role == role:
                    game.add_history(f"Début du tour des loup-garous ({player_list})", show=False)
                    player_list.append(player)
                    try:
                        await game.announce("urturn_" + role, author=player.member,
                                        mp=True, image=player.role.image)
                    except KeyError:
                        game.logger.error(f"Key Error on uturn_{role}")
            await function(game, player_list)
        return wrapper
    return deco_wrap