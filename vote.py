import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)


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


async def start_voting(ctx):
    message = await ctx.send('Which team won?')
    await message.add_reaction("⬅")
    await message.add_reaction("➡")
    return message


async def count_if_votes_efficient(left, right, first_team_players, second_team_players):
    all_players = (first_team_players + second_team_players)
    if len(left) >= 0.75 * len(all_players):
        return True, first_team_players, second_team_players
    elif len(right) >= 0.75 * len(all_players):
        return True, second_team_players, first_team_players
    else:
        return False, None, None


async def force_admin_decision(reaction, first_team_players, second_team_players):
    if str(reaction.emoji) == "⬅":
        return first_team_players, second_team_players
    if str(reaction.emoji) == "➡":
        return second_team_players, first_team_players
