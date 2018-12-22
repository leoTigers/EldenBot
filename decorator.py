from random_message import forbidden

OWNER_ID = 384274248799223818
OFFICIAL_SERVS = [367683573014069249]
SERV_FORBIDEN = "Impossible de lancer cette commande sur ce serveur"


def not_offical_serv(func):
    async def wrapper(self, *args, channel, guild, force, **kwargs):
        if not guild or force or guild.id not in OFFICIAL_SERVS:
            await func(self, *args, channel=channel, guild=guild, force=force,
                       **kwargs)
        else:
            await channel.send(SERV_FORBIDEN)
    return wrapper

def only_owner(func):
    async def wrapper(self, *args, member, channel, **kwargs):
        if member.id == OWNER_ID:
            await func(self, *args, member=member, channel=channel, **kwargs)
        else:
            await channel.send(forbidden(message, who="only_owner"))
    return wrapper

def can_manage_message(func):
    async def wrapper(self, *args, channel, member, guild, force, **kwargs):
        if not guild:
            await channel.send("la commande doit être utilisé sur un serveur.")
            return
        perms = member.permissions_in(channel)
        if perms.manage_messages or force:
            await func(self, *args, channel=channel, member=member, guild=guild,
                       force=force, **kwargs)
        else:
            pass
    return wrapper
