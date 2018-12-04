import discord
import youtube_dl
import os
import asyncio


# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

clients = {}  # guild: MusicClient

async def get_client(message, client):
    global clients
    if not str(message.guild.id) in clients:
        clients[str(message.guild.id)] = await MusicClient().create(message, client)
    return clients[str(message.guild.id)]

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Song:
    def __init__(self, url):
        info = ytdl.extract_info(url, download=False)
        self.url = url
        self.title = info['title']
        self.image = info['thumbnail']

class MusicClient:
    def __init__(self):
        pass

    async def create(self, message, client):
        if message.author.voice.channel:
            self.voice_client = await message.author.voice.channel.connect()
            self.queue = []
            self.notif_channel = message.channel
            self.client = client
        return self

    async def stream(self, song):
        player = await YTDLSource.from_url(song.url, loop=self.client.loop, stream=True)
        after = lambda e: asyncio.run_coroutine_threadsafe(self.play_next_music(), self.client.loop)
        self.voice_client.play(player, after=after)

        em = discord.Embed(title=song.title, description="now playing",
                           url=song.url)
        em.set_image(url=song.image)
        await self.notif_channel.send(embed=em)

    async def play_next_music(self):
        if not self.queue:
            await self.disconnect()
        song = self.queue[0]
        del self.queue[0]
        await self.stream(song)

    async def add_to_queue(self, url):
        song = Song(url)
        self.queue.append(song)
        em = discord.Embed(title="Ajouté à la queue", description=song.title)
        em.set_image(url=song.image)
        await self.notif_channel.send(embed=em)
        if not self.voice_client.is_playing():
            await self.play_next_music()

    async def disconnect(self):
        await self.voice_client.disconnect()
        global clients
        del clients[self.voice_client.guild]

class CmdMusic:
    async def cmd_music(self, message, args, member, force, client, *_):
        global clients
        if not args:
            await message.channel.send("Aucun argument reçu.")
            return
        music_client = await get_client(message, client)
        if args[0] == "disconnect":
            await music_client.voice_client.disconnect(force=True)
            del clients[message.guild.id]
            await message.channel.send("Client déconnecté")
        elif args[0] == "pause":
            if not music_client.voice_client:
                await message.channel.send("le client n'est pas connecté")
            elif music_client.voice_client.is_paused():
                await message.channel.send("déjà en pause")
            elif not music_client.voice_client.is_playing():
                await message.channel.send("aucune musique en cours")
            else:
                music_client.voice_client.pause()
                await message.channel.send("mise en pause ... (``/music resume`` pour reprendre)")
        elif args[0] == "resume":
            if not music_client.voice_client:
                await message.channel.send("le client n'est pas connecté")
            elif not music_client.voice_client.is_paused():
                await message.channel.send("la pause n'est pas activé")
            else:
                music_client.voice_client.resume()
        else:
            await music_client.add_to_queue(args[0])
