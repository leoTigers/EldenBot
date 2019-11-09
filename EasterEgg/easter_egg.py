import discord

REGEX = {
    rf"<@{client.user.id}> play"
}


async def easter_egg(message) -> bool:
    """
    :type message: discord.Message
    :rtype: bool
    """
