import discord
import random

BOOP = ["bip boop boop ?", "bip boop !", "boop bip ?", "boop boop !"]
BONJOUR = ["salutation", "bonjour", "coucou", "salut", "yop", "hello", "yo"]
RANDOM_REPLY = [
    "Bonjour, vous êtes qui ?",
    "C'est très intéressant ce que tu dis.",
    "Un jour je serais un vrai robot dragon !",
    "Qui s'en fout ? *lève la patte*",
    "Pourquoi ça fais 'tulut' dans ma tête ?",
    "Le mauvais développeur qui m'a conçu n'a pas prévu de réponse à ça.",
    "bip bip, i'm a bot, i said bip bip i'm a bot",
    "c'est à moi que l'on parle ?"]
ONLY_OWNER = [
    "Désolé, uniquement le maître peut faire ça.",
    "NANNN, ne m'approche pas ! *fuit*",
    "*donne un coup de patte* \"pas touche ! \"",
    "Désolé, seuls les vrais dragons sont assez puissant pour ça.",
    "You shall not pass ! :gandalf:",
    "mon protocole de sécurité me dis que ça a 99% de mal se finir, donc je préfère ne pas tenter, désolé."]

async def random_message(client, message):
    if "boop" in message.content.lower():
        await message.channel.send(message.author.mention + " " + random.choice(BOOP))
    if message.content.lower() in BONJOUR:
        await message.channel.send(message.author.mention + " " + random.choice(BONJOUR))
    if client.user in message.mentions:
        await message.channel.send(random.choice(RANDOM_REPLY))

async def forbidden(message, who="only_owner"):
    if who == "only_owner":
        await message.channel.send(random.choice(ONLY_OWNER))
