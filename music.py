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
                voice.stop()
                await voice.disconnect()
                await message.channel.send("Client déconnecté")
                voice = None
            else:
                await message.channel.send("Le client est déjà déconnecté")
        elif args[0] == "pause":
            if not voice:
                await message.channel.send("le client n'est pas connecté")
            elif voice.is_paused():
                await message.channel.send("déjà en pause")
            elif not voice.is_playing():
                await message.channel.send("aucune musique en cours")
            else:
                voice.pause()
                await message.channel.send("mise en pause ...")
        elif args[0] == "resume":
            if not voice:
                await message.channel.send("le client n'est pas connecté")
            elif not voice.is_paused():
                await message.channel.send("la pause n'est pas activé")
            else:
                voice.resume()
        else:
            if not voice or not voice.is_connected():
                channel = get_client_channel(message.guild, member)
                voice = await channel.connect()
