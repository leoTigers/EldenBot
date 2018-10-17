import discord
import ctypes
from pytube import YouTube




def get_client_channel(guild, target_member):
    channels = guild.voice_channels
    for channel in channels:
        if target_member in channel.members:
            return channel


class CmdMusic:
    def __init__(self):
        self.opus_lib = discord.opus.load_opus(ctypes.util.find_library('opus'))
        self.voice = None
        self.queue = []
    async def cmd_music(self, message, args, member, *_):
        if not args:
            await message.channel.send("Aucun argument reçu.")
            return
        if args[0] == "disconnect":
            if self.voice:
                self.voice.stop()
                await self.voice.disconnect()
                await message.channel.send("Client déconnecté")
                self.voice = None
            else:
                await message.channel.send("Le client est déjà déconnecté")
        elif args[0] == "pause":
            if not self.voice:
                await message.channel.send("le client n'est pas connecté")
            elif self.voice.is_paused():
                await message.channel.send("déjà en pause")
            elif not self.voice.is_playing():
                await message.channel.send("aucune musique en cours")
            else:
                self.voice.pause()
                await message.channel.send("mise en pause ...")
        elif args[0] == "resume":
            if not self.voice:
                await message.channel.send("le client n'est pas connecté")
            elif not self.voice.is_paused():
                await message.channel.send("la pause n'est pas activé")
            else:
                self.voice.resume()
        else:
            if not self.voice or not self.voice.is_connected():
                channel = get_client_channel(message.guild, member)
                self.voice = await channel.connect()
            music = YouTube(args[0]).streams.filter(only_audio=True).first()
            audio_source = discord.PCMAudio(music)
            self.voice.play(audio_source)
