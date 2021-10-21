from match import *
from raterapi_requests import *
from command_responses import *
from helpers import *
from stats import *

load_dotenv()

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
    error_msg = validate_teams(ctx.message)
    if error_msg:
        await ctx.send(error_msg)
        return
    message = await start_voting(ctx)
    first_team_players, second_team_players = await fetch_first_and_second_team(ctx)

    @bot.event
    async def on_reaction_add(reaction, user, non_efficient_votes=None):
        if is_bot(user):
            return
        if user.permissions_in(ctx.channel).administrator:
            winners, losers = await force_admin_decision(reaction, first_team_players, second_team_players)
            await execute_result(losers, winners)
        else:
            if is_bot(user):
                return
            voting_pool = await ctx.fetch_message(message.id)
            left, right = await vote(voting_pool, first_team_players, second_team_players)
            is_efficient, winners, losers = await count_if_votes_efficient(left, right, first_team_players,
                                                                           second_team_players)
            if is_efficient:
                await execute_result(losers, winners)
            else:
                if not non_efficient_votes:
                    non_efficient_votes = await ctx.send('Admin or 75% of the players must agree on the match result ')

    async def execute_result(losers, winners):
        await message.delete()
        msg = await create_match(winners, losers, ctx.guild.id)
        await ctx.send(msg)


@bot.command(pass_context=True, aliases=['stat', 'level', 'rank', 'Rank', 'Stat', 'Level', 'lvl'])
@commands.cooldown(2, 1, commands.BucketType.guild)
async def stats(ctx):
    player = await fetch_user_who_got_mentions_or_message_author(ctx.message)
    msg = await get_player_stats(player, ctx.guild.id)
    await ctx.send(msg)


@bot.command(
    pass_context=True,
    aliases=['leaderboard', 'levels', 'ranks', 'top', 'Leaderboard',
             'leader', 'lvls', 'ranking', 'Ranking', 'Top', 'best'])
@commands.cooldown(2, 1, commands.BucketType.guild)
async def rankings(ctx):
    page = 1
    leaderboard = await get_leaderboard(ctx.guild.id, ctx.message.author)
    if leaderboard is None:
        await ctx.send("not enough games played in the server yet")
    else:
        message = await ctx.send(leaderboard)
        await message.add_reaction("⬅")
        await message.add_reaction("➡")

    @bot.event
    async def on_reaction_add(reaction, user):
        if user == bot.user or message is None:
            return
        if str(reaction.emoji) == "⬅":
            await message.edit(content=await get_leaderboard(ctx.guild.id, ctx.message.author, page - 1))
        if str(reaction.emoji) == "➡":
            await message.edit(content=await get_leaderboard(ctx.guild.id, ctx.message.author, page + 1))


"""
FUNCTIONS
"""


# TODO move functions to other files


async def create_match(winners, losers, guild_id):
    new_match = await match_factory(winners, losers)
    res = await create_match_request(guild_id, new_match)
    msg = await create_match_response(res)
    return msg


async def get_leaderboard(guild_id, author, page=1):
    if page < 1:  # in case user asked for previous page when his is on the first page
        page = 1
    leaderboard = await get_leaderboard_request(guild_id, page)
    # validate page exist
    if not leaderboard["data"]:
        return None
    rank_on_server = (await get_user_rank_request(guild_id, author))["rank"]["rank"]
    return await create_leaderboard_response(author, leaderboard, rank_on_server)


async def find_user(name):
    return discord.utils.find(lambda n: str(n) == name, bot.get_all_members())


bot.run(getenv("DISCORD_API"))
