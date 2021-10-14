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


def validate_teams(ctx):
    if len(ctx.message.mentions) == 1:
        # only the bot got mentions
        return "mentions the players and separate between them with `vs` according to their tea,"

    if len(ctx.message.mentions) == 2:
        # only 1 player
        return "mention both opponent in same line please, and separate them with `vs` "

    if "vs" not in ctx.message.content:
        return "separate the 2 teams with `vs` in between"
    if (len(ctx.message.mentions) - 1) % 2 != 0:
        return "uneven teams"


async def create_match(winners, losers, guild_id, ctx):
    match_data = {
        "teams": [
            {
                "users": winners,
                "result": 1
            },
            {
                "users": losers,
                "result": 0
            }
        ]
    }
    res = req.post(
        RaterApi + "/games/" + str(guild_id) + "/matches",
        json=match_data,
        headers=auth_headers
    )
    data = dict(res.json())
    msg = "**New Ratings**\n"
    for user in data["users"]:
        user_name = (user["name"].split("#"))[0]
        user_discriminator = (user["name"].split("#"))[1]
        user_mention = discord.utils.get(bot.get_all_members(), name=user_name, discriminator=user_discriminator)
        msg += f"{user_mention.mention}" + "\n" + "`Rank : " + user["rank"][
            "rank"] + " " + str(round(user["rank"]["points"])) + " LP" + "\n" + "Rating : " + str(
            round(user["rating"])) + "`\n"
    await ctx.send(msg)


def add_server(guild_id):
    req.post(
        RaterApi + "/games",
        {"name": str(guild_id)},
        headers=auth_headers
    )


def remove_server(guild_id):
    req.delete(RaterApi + "/games/" + str(guild_id), headers=auth_headers)


@bot.event
async def on_guild_join(guild):
    add_server(guild.id)


@bot.event
async def on_guild_remove(guild):
    remove_server(guild.id)


@bot.command(pass_context=True, aliases=["rate", "play"])
@commands.cooldown(1, 1, commands.BucketType.guild)
async def match(ctx):
    error_msg = validate_teams(ctx)
    if error_msg is not None:
        await ctx.send(error_msg)
    else:
        message = await ctx.send('Which team won?')
        await message.add_reaction("⬅")
        await message.add_reaction("➡")
    mentions_len = len(ctx.message.mentions) - 1
    team_1 = ctx.message.mentions[1: (mentions_len // 2) + 1]
    team_2 = ctx.message.mentions[mentions_len // 2 + 1:]
    team_1_players = list()
    team_2_players = list()
    for idx, val in enumerate(team_1):
        team_1_players.append(team_1[idx].name + "#" + team_1[idx].discriminator)
        team_2_players.append(team_2[idx].name + "#" + team_2[idx].discriminator)

    @bot.event
    async def on_reaction_add(reaction, user):
        if user == bot.user:
            return
        if user.permissions_in(ctx.channel).administrator:
            if str(reaction.emoji) == "⬅":
                await message.delete()
                await create_match(team_1_players, team_2_players, ctx.guild.id, ctx)
            if str(reaction.emoji) == "➡":
                await message.delete()
                await create_match(team_2_players, team_1_players, ctx.guild.id, ctx)
        else:
            message2 = ""
            users = set()
            left = set()
            right = set()
            message1 = await ctx.fetch_message(message.id)
            for reaction in message1.reactions:
                if reaction.emoji == "⬅":
                    async for user in reaction.users():
                        if user != bot.user:
                            left.add(user)
                            users.add(user)
                if reaction.emoji == "➡":
                    async for user in reaction.users():
                        if user != bot.user:
                            right.add(user)
            if len(left) >= 0.75 * len(users):
                await message.delete()
                await create_match(team_1_players, team_2_players, ctx.guild.id, ctx)
            elif len(right) >= 0.75 * len(users):
                await message.delete()
                await create_match(team_1_players, team_2_players, ctx.guild.id, ctx)
            else:
                if message2 == "":
                    message2 = await ctx.send('The winner must be agreed upon by 75% or more of the players')


async def get_player_stats(message, guild_id, ctx):
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
            guild_id) + "/ranking/" + slugify(player.name) + player.discriminator + "?maxRatingDeviation=150",
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
    await ctx.send(msg)


@bot.command(pass_context=True, aliases=['stats', 'level', 'rank','Rank','Stat','Level','lvl'])
@commands.cooldown(2, 1, commands.BucketType.guild)
async def stat(ctx):
    await get_player_stats(ctx.message, ctx.guild.id, ctx)


async def get_leaderboard(guild_id, author, page=1):
    if page < 1:  # in case user asked for previous page when his is on the first page
        page = 1
    res = req.get(
        RaterApi + "/games/" + str(
            guild_id) + "/ranking/" + slugify(author.name) + author.discriminator + "?maxRatingDeviation=150",
        headers=auth_headers
    )
    rank = res.json()["rank"]["rank"]
    res = req.get(
        RaterApi + "/games/" + str(guild_id) + f"/ranking/?maxRatingDeviation=150&page={page}",
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


@bot.command(pass_context=True, aliases=['leaderboard', 'levels', 'ranks', 'top', 'best', 'leader', 'lvls', 'ranking'])
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


bot.run(getenv("DISCORD_API"))
