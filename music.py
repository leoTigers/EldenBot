import discord
import youtube_dl
import os

def download(title, video_url):
    ydl_opts = {
        'outtmpl': '{}.%(ext)s'.format(title),
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '96',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
    return {
        'audio': open('musicqueue/{}.mp3'.format(title), 'rb'),
        'title': title,
    }

def get_client_channel(guild, target_member):
    channels = guild.voice_channels
    for channel in channels:
        if target_member in channel.members:
            return channel


class CmdMusic:
    def __init__(self):
        self.voice = None
        self.queue = []

    def play_next_music(self, *_):
        if not self.queue:
            return self.disconnect
        music = self.queue[0]
        del self.queue[0]
        audio_source = discord.FFmpegPCMAudio("musicqueue/" + music + ".mp3")
        self.voice.play(audio_source, after=self.play_next_music)
        self.delete_file

    async def disconnect(self):
        self.voice.stop()
        await self.voice.disconnect()
        self.voice = None
        self.queue = []
        self.delete_file

    def delete_file(self):
        for file in os.listdir("musicqueue"):
            if file not in self.queue:
                os.remove("musiquequeue/" + file)

    async def cmd_music(self, message, args, member, *_):
        if not args:
            await message.channel.send("Aucun argument reçu.")
            return

        if args[0] == "disconnect":
            if self.voice:
                await self.disconnect()
                await message.channel.send("Client déconnecté")
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
            # add to the queue
            with youtube_dl.YoutubeDL({}) as ydl:
                info = ydl.extract_info(args[0], download=False)
            em = discord.Embed(title="Ajouté à la queue",
                               description=info['title'],
                               colour=0xCC0000)
            print(info['thumbnail'])
            em.set_author(name=member.name, icon_url=member.avatar_url)
            em.set_image(url=info['thumbnail'])
            await message.channel.send(embed=em)
            self.queue.append(download(info['title'], args[0])['title'])
            if not self.voice.is_playing() and not self.voice.is_paused():
                self.play_next_music()
