import discord
from discord.ext import commands

intents = discord.Intents.default()
bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)


def is_bot(user):
    return user == bot.user


async def fetch_user_who_got_mentions_or_message_author(message):
    mentions = message.mentions
    if len(mentions) > 1:  # a user got mentioned
        player = mentions[1]
    else:
        player = message.author
    return player
