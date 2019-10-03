from random_message import forbidden
import logging

OWNER_ID = 384274248799223818
OFFICIAL_SERVS = [367683573014069249]
SERV_FORBIDEN = "Impossible de lancer cette commande sur ce serveur"
logger = logging.getLogger("Decorator")


def not_offical_serv(func):
    async def wrapper(self, *args, channel, guild, force, **kwargs):
        if not guild or force or guild.id not in OFFICIAL_SERVS:
            await func(self, *args, channel=channel, guild=guild, force=force,
                       **kwargs)
        else:
            await channel.send(SERV_FORBIDEN)
    return wrapper

def only_owner(func):
    async def wrapper(self, *args, member, channel, message, **kwargs):
        if member.id == OWNER_ID:
            await func(self, *args, member=member, channel=channel, message=message, **kwargs)
        else:
            await forbidden(message, who="only_owner")
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

def can_manage_role(func):
    async def wrapper(self, *args, channel, **kwargs):
        if not kwargs['guild']:
            await channel.send("la commande doit être utilisé sur un serveur.")
            return
        if kwargs['member'].guild_permissions.manage_roles or kwargs['force']:
            await func(self, *args, channel=channel, **kwargs)
        else:
            await kwargs['channel'].send("La permission 'Gérer les roles' est nécéssaire")
    return wrapper

def refresh_google_token(creds, gc):
    def decorat(func):
        async def wrapper(*args, **kwargs):
            logger.debug("Checking for Google token ...")
            logger.debug(f"testing creds.access_token_expired : value = {creds.access_token_expired}")
            if creds.access_token_expired:
                logger.info("Refreshing google token")
                gc.login()
            return await func(*args, **kwargs)
        return wrapper
    return decorat