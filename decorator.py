from random_message import forbidden

OWNER_ID = 384274248799223818
OFFICIAL_SERVS = [367683573014069249]
SERV_FORBIDEN = "Impossible de lancer cette commande sur ce serveur"


def not_offical_serv(func):
    async def wrapper(self, message, args, member, force, *args_, **kwargs):
        guild = message.guild
        if not guild or force or guild.id not in OFFICIAL_SERVS:
            await func(self, message, args, member, force, *args_, **kwargs)
        else:
            await message.channel.send(SERV_FORBIDEN)
    return wrapper

def only_owner(func):
    async def wrapper(self, message, *args, **kwargs):
        if message.author.id == OWNER_ID:
            await func(self, message, *args, **kwargs)
        else:
            await message.channel.send(forbidden(message, who="only_owner"))
    return wrapper
