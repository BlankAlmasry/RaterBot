from collections import namedtuple
from os import getenv
import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)
RaterApi = "https://raterapi.azurewebsites.net/"
auth_headers = {"Authorization": "Bearer " + getenv('RATER_API')}


async def match_factory(winners, losers):
    Match = namedtuple("Match", "teams")
    match_data = Match([
        {"users": winners, "result": 1},
        {"users": losers, "result": 0}
    ])
    return match_data._asdict()


def validate_teams(message):
    if len(message.mentions) == 1:
        # only the bot got mentions
        return "mentions the players and separate between them with `vs` according to their tea,"

    if len(message.mentions) == 2:
        # only 1 player
        return "mention both opponent in same line please, and separate them with `vs` "

    if "vs" not in message.content:
        return "separate the 2 teams with `vs` in between"

    # Lazy validation, would fix an early `vs` or a late one by auto-balancing teams
    if (len(message.mentions) - 1) % 2 != 0:
        return "uneven teams"
