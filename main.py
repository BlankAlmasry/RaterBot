from match import *
from rankings import paginate_rankings, get_rankings
from raterapi_requests import *
from responses import *
from helpers import *
from stats import *
from vote import *

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
        message, first_team_players, second_team_players = await make_match(ctx)
    except ValueError:  # command validation failed
        return

    @bot.event
    async def on_reaction_add(reaction, user):
        if user == bot.user:
            return
        await match_voting_pool_handler(
            message, first_team_players, second_team_players,
            ctx, reaction, user)


@bot.command(pass_context=True, aliases=['stat', 'level', 'rank', 'Rank', 'Stat', 'Level', 'lvl'])
@commands.cooldown(2, 1, commands.BucketType.guild)
async def stats(ctx):
    await get_stats(ctx)


@bot.command(
    pass_context=True,
    aliases=['leaderboard', 'levels', 'ranks', 'top', 'Leaderboard',
             'leader', 'lvls', 'ranking', 'Ranking', 'Top', 'best'])
@commands.cooldown(2, 1, commands.BucketType.guild)
async def rankings(ctx):
    page, message = await get_rankings(ctx)

    @bot.event
    async def on_reaction_add(reaction, user):
        if user == bot.user or message is None:
            return
        await paginate_rankings(ctx, reaction, message, page)


bot.run(getenv("DISCORD_API"))
