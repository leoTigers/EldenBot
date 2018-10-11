voice = None
queue = []


def get_client_channel(guild, target_member):
    channels = guild.voice_channels
    for channel in channels:
        if target_member in channel.members:
            return channel


class CmdMusic:
    async def cmd_music(self, message, args, member, *_):
        if not args:
            await message.channel.send("Aucun argument reçu.")
            return
        if args[0] == "disconnect":
            if voice:
                await self.disconnect()
                await message.channel.send("Client déconnecté")
            else:
                await message.channel.send("Le client est déjà déconnecté")
        else:
            if not voice or not voice.is_connected():
                channel = get_client_channel(message.guild, member)
                voice = await channel.connect()
