from voice_client import VoiceClient


class LeagueVoiceGame:
    async def __init__(self, channel, author, client):
        self.channel = channel
        self.score = {}
        self.voice = VoiceClient()
        if a
        self.voice = author.voice.channel.connect()
    async def run(self):
        pass


class CmdLeagueVoice:
    def cmd_leaguevoice(self, message, args, member, force, client):
        leaguevoice = await LeagueVoiceGame()
        await leaguevoice.run()
