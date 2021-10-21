from slugify import slugify
from match import *

load_dotenv()

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)
RaterApi = "https://raterapi.azurewebsites.net/"
auth_headers = {"Authorization": "Bearer " + getenv('RATER_API')}


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


@bot.command(pass_context=True, aliases=['stat', 'stats', 'level', 'rank', 'Rank', 'Stat', 'Level', 'lvl'])
@commands.cooldown(2, 1, commands.BucketType.guild)
async def stat(ctx):
    msg = await get_player_stats(ctx.message, ctx.guild.id)
    await ctx.send(msg)

@bot.command(
    pass_context=True,
    aliases=['leaderboard', 'levels', 'ranks', 'top', 'Leaderboard',
             'leader', 'lvls', 'ranking', 'Ranking', 'Top', 'best'])
@commands.cooldown(2, 1, commands.BucketType.guild)
async def rankings(ctx):
    page = 1
    message = await get_leaderboard(ctx.guild.id, ctx.message.author)
    if message is None:
        await ctx.send("not enough games played in the server yet")
    else:
        await ctx.send(message)
    await message.add_reaction("⬅")
    await message.add_reaction("➡")

    @bot.event
    async def on_reaction_add(reaction, user):
        if user == bot.user:
            return
        if message is None:
            return
        if user.permissions_in(ctx.channel).administrator:
            if str(reaction.emoji) == "⬅":
                await message.edit(content=await get_leaderboard(ctx.guild.id, ctx.message.author, page - 1))
            if str(reaction.emoji) == "➡":
                await message.edit(content=await get_leaderboard(ctx.guild.id, ctx.message.author, page + 1))


async def get_player_stats(message, guild_id):
    mentions = message.mentions
    if len(mentions) > 1:  # a user got mentioned
        player = mentions[1]
    else:
        player = message.author
    res = req.get(
        RaterApi + "/games/" + str(guild_id) + "/users/" + slugify(player.name) + player.discriminator,
        headers=auth_headers
    )
    res1 = req.get(
        RaterApi + "/games/" + str(
            guild_id) + "/ranking/" + slugify(player.name) + player.discriminator + "?maxRatingDeviation=200",
        headers=auth_headers
    )
    player = res.json()
    player_rank = res1.json()
    msg_res1 = ""
    if not player_rank['rank']['rank'] is None:
        msg_res1 = f"`Leaderboard: {player_rank['rank']['rank']}th Over {player_rank['rank']['all']} players`"
    else:
        msg_res1 = "`Leaderboard: not enough games yet`"

    msg = f"`Rank: {player['rank']['rank']}`\n" \
          f"`Rating: {int(player['rating'])}{'?' if player_rank['rank']['rank'] is None else ''}`\n" \
          f"`Win/Loses: {player['wins']}/{player['loses']}`\n" \
          f"`Win Ratio: {round((player['wins'] / (player['loses'] + player['wins'])) * 100, 2)}%`\n" \
          f"{msg_res1}"
    return msg


"""
FUNCTIONS
"""


# TODO move functions to other files

async def create_match(winners, losers, guild_id):
    new_match = await match_factory(winners, losers)
    res = await create_match_request(guild_id, new_match)
    msg = await create_match_response(res)
    return msg


async def create_match_response(data):
    data = dict(data.json())
    msg = "**New Ratings**\n"
    for user in data["users"]:
        user_mention = discord.utils.find(lambda n: str(n) == user["name"], bot.get_all_members())
        msg += f"{user_mention.mention}" + "\n" + "`Rank : " + user["rank"][
            "rank"] + " " + str(round(user["rank"]["points"])) + " LP" + "\n" + "Rating : " + str(
            round(user["rating"])) + "`\n"
    return msg


def add_server_request(guild_id):
    req.post(
        RaterApi + "/games",
        {"name": str(guild_id)},
        headers=auth_headers
    )


def remove_server_request(guild_id):
    req.delete(RaterApi + "/games/" + str(guild_id), headers=auth_headers)


async def start_voting(ctx):
    message = await ctx.send('Which team won?')
    await message.add_reaction("⬅")
    await message.add_reaction("➡")
    return message


async def fetch_first_and_second_team(ctx):
    mentions_len = len(ctx.message.mentions) - 1
    team_1 = ctx.message.mentions[1: (mentions_len // 2) + 1]
    team_2 = ctx.message.mentions[mentions_len // 2 + 1:]
    first_team_players = tuple(map(lambda player: player.name + "#" + player.discriminator, team_1))
    second_team_players = tuple(map(lambda player: player.name + "#" + player.discriminator, team_2))
    return first_team_players, second_team_players


async def force_admin_decision(reaction, first_team_players, second_team_players):
    if str(reaction.emoji) == "⬅":
        return first_team_players, second_team_players
    if str(reaction.emoji) == "➡":
        return second_team_players, first_team_players


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


async def get_leaderboard(guild_id, author, page=1):
    if page < 1:  # in case user asked for previous page when his is on the first page
        page = 1
    res = req.get(
        RaterApi + "/games/" + str(
            guild_id) + "/ranking/" + slugify(author.name) + author.discriminator + "?maxRatingDeviation=200",
        headers=auth_headers
    )
    rank = res.json()["rank"]["rank"]
    res = req.get(
        RaterApi + "/games/" + str(guild_id) + f"/ranking/?maxRatingDeviation=200&page={page}",
        headers=auth_headers
    )
    leaderboard = res.json()
    if not leaderboard["data"]:
        return None
    header = "`     #Name       #Rank              #Rating \n"
    body = ""
    for index, user in enumerate(leaderboard["data"]):
        index = index + (leaderboard['meta']['current_page'] - 1) * 10
        user_msg = f" #{index + 1}{' ' * (4 - len(str(index + 1)))}" + \
                   f"{user['name'].split('#')[0]}{' ' * (12 - len(user['name'].split('#')[0]))}" \
                   f"{user['rank']['rank']}{' ' * (19 - len(user['rank']['rank']))}" \
                   f"{round(user['rating'])}   \n"
        body += user_msg
    footer = f"   Page {leaderboard['meta']['current_page']}" \
             f" of {leaderboard['meta']['last_page']} •" \
             f" Your Rank: {rank if rank is not None else '?'} •  {author.name}" \
             f"{' ' * (13 - len(author.name) - len(str(leaderboard['meta']['current_page'])) - len(str(leaderboard['meta']['current_page'])))}`"
    return header + body + footer


def is_bot(user):
    return user == bot.user


bot.run(getenv("DISCORD_API"))
