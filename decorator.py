from random_message import forbidden

OWNER_ID = 384274248799223818
OFFICIAL_SERVS = [367683573014069249]
SERV_FORBIDEN = "Impossible de lancer cette commande sur ce serveur"


def not_offical_serv(func):
    async def wrapper(message, *args, **kwargs):
        guild_id = message.guild.id
        if guild.id not in OFFICIAL_SERVS:
            await func(message, *args, **kwargs)
        else:
            await message.channel.send(SERV_FORBIDEN)
    return wrapper

def only_owner(func):
    async def wrapper(message, *args, **kwargs):
        if message.author.id != OWNER_ID:
            await func(message, *args, **kwargs)
        else:
            await message.channel.send(forbidden(message), who="only_owner")
    return wrapper
