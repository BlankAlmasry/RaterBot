from collections import namedtuple
from os import getenv
import discord
from dotenv import load_dotenv
from discord.ext import commands

from helpers import find_user
from raterapi_requests import create_match_request

load_dotenv()

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)
RaterApi = "https://raterapi.azurewebsites.net/"
auth_headers = {"Authorization": "Bearer " + getenv('RATER_API')}


# TODO move functions to other files

async def create_match(winners, losers, guild_id, users):
    new_match = await match_factory(winners, losers)
    res = await create_match_request(guild_id, new_match)
    msg = await create_match_response(res, users)
    return msg


async def create_match_response(data, users):
    msg = "**New Ratings**\n"
    for user in data["users"]:
        user_mention = await find_user(user["name"], users)
        msg += f"{user_mention.mention}" + "\n" + "`Rank : " + user["rank"][
            "rank"] + " " + str(round(user["rank"]["points"])) + " LP" + "\n" + "Rating : " + str(
            round(user["rating"])) + "`\n"
    return msg


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


async def count_if_votes_efficient(left, right, first_team_players, second_team_players):
    all_players = (first_team_players + second_team_players)
    if len(left) >= 0.75 * len(all_players):
        return True, first_team_players, second_team_players
    elif len(right) >= 0.75 * len(all_players):
        return True, second_team_players, first_team_players
    else:
        return False, None, None


async def vote(voting_pool, first_team_players, second_team_players):
    all_players = (first_team_players + second_team_players)
    left = set()
    right = set()
    for reaction in voting_pool.reactions:
        if reaction.emoji == "⬅":
            async for user in reaction.users():
                if user != bot.user and \
                        user.name + "#" + user.discriminator in all_players:
                    left.add(user)
        if reaction.emoji == "➡":
            async for user in reaction.users():
                if user != bot.user and \
                        user.name + "#" + user.discriminator in all_players:
                    right.add(user)
    return tuple(left), tuple(right)


async def force_admin_decision(reaction, first_team_players, second_team_players):
    if str(reaction.emoji) == "⬅":
        return first_team_players, second_team_players
    if str(reaction.emoji) == "➡":
        return second_team_players, first_team_players


async def fetch_first_and_second_team(ctx):
    mentions_len = len(ctx.message.mentions) - 1
    team_1 = ctx.message.mentions[1: (mentions_len // 2) + 1]
    team_2 = ctx.message.mentions[mentions_len // 2 + 1:]
    first_team_players = tuple(map(lambda player: player.name + "#" + player.discriminator, team_1))
    second_team_players = tuple(map(lambda player: player.name + "#" + player.discriminator, team_2))
    return first_team_players, second_team_players


async def start_voting(ctx):
    message = await ctx.send('Which team won?')
    await message.add_reaction("⬅")
    await message.add_reaction("➡")
    return message
