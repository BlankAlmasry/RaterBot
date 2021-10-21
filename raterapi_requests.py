from os import getenv
import discord
from dotenv import load_dotenv
from discord.ext import commands
import requests as req
from slugify import slugify

load_dotenv()

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)
RaterApi = "https://raterapi.azurewebsites.net/"
auth_headers = {"Authorization": "Bearer " + getenv('RATER_API')}


async def get_user_rank_request(guild_id, player):
    return req.get(
        RaterApi + "/games/" + str(
            guild_id) + "/ranking/" + slugify(player.name) + player.discriminator + "?maxRatingDeviation=200",
        headers=auth_headers
    ).json()


async def create_match_request(guild_id, match_data):
    res = req.post(
        RaterApi + "/games/" + str(guild_id) + "/matches",
        json=match_data,
        headers=auth_headers
    )
    return res


async def get_user_stats_request(guild_id, player):
    return req.get(
        RaterApi + "/games/" + str(guild_id) + "/users/" + slugify(player.name) + player.discriminator,
        headers=auth_headers
    ).json()


def add_server_request(guild_id):
    req.post(
        RaterApi + "/games",
        {"name": str(guild_id)},
        headers=auth_headers
    )


def remove_server_request(guild_id):
    req.delete(RaterApi + "/games/" + str(guild_id), headers=auth_headers)


async def get_leaderboard_request(guild_id, page):
    return req.get(
        RaterApi + "/games/" + str(guild_id) + f"/ranking/?maxRatingDeviation=200&page={page}",
        headers=auth_headers
    ).json()
