import discord
from discord.ext import commands
from bot.leaderboard.leaderboard_facade import print_leaderboard, try_paginate_leaderboard
from bot.raterapi_requests import *
from bot.stats.stats_facade import print_stats
from bot.match.match_facade import *

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)


@bot.event
async def on_guild_join(guild):
    add_server_request(guild.id)


@bot.event
async def on_guild_remove(guild):
    remove_server_request(guild.id)


@bot.command(pass_context=True, aliases=["rate", "play", "team", 'fight'])
@commands.cooldown(1, 1, commands.BucketType.guild)
async def match(ctx):
    try:
        voting_pool, first_team_players, second_team_players = await start_match(ctx)
    except ValueError:  # command validation failed
        return

    @bot.event
    async def on_reaction_add(reaction, user):
        if user == bot.user:
            return
        await add_vote(
            voting_pool, first_team_players, second_team_players,
            ctx, reaction, user)


@bot.command(pass_context=True, aliases=['stat', 'level', 'rank', 'Rank', 'Stat', 'Level', 'lvl'])
@commands.cooldown(2, 1, commands.BucketType.guild)
async def stats(ctx):
    await print_stats(ctx)


@bot.command(
    pass_context=True,
    aliases=['ranking', 'levels', 'ranks', 'top', 'Leaderboard',
             'leader', 'lvls', 'Ranking', 'Top', 'best', 'rankings'])
@commands.cooldown(2, 1, commands.BucketType.guild)
async def leaderboard(ctx):
    current_page, leaderboard_message = await print_leaderboard(ctx)

    @bot.event
    async def on_reaction_add(reaction, user):
        if user == bot.user or leaderboard_message is None:
            return
        # will paginate if user reacted with pagination arrows
        await try_paginate_leaderboard(ctx, reaction, leaderboard_message, current_page)


bot.run(getenv("DISCORD_API"))
