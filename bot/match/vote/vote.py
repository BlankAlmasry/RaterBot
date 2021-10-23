from discord.ext import commands
import bot.match.match_facade as match_facade

bot = commands.Bot(command_prefix=commands.when_mentioned)


async def start_voting(ctx):
    message = await ctx.send('Which team won?')
    await message.add_reaction("⬅")
    await message.add_reaction("➡")
    return message


async def vote(message, first_team_players, second_team_players,
               ctx, reaction, user):
    # if admin voted, force his vote to be the winner
    if user.permissions_in(ctx.channel).administrator:
        winners, losers = await get_admin_decision(reaction, first_team_players, second_team_players)
        await match_facade.execute_result(ctx, message, losers, winners)
    else:
        voting_pool = await ctx.fetch_message(message.id)
        first_team_won_voters, second_team_won_voters = await count_votes(voting_pool,
                                                                          first_team_players,
                                                                          second_team_players)
        is_efficient, winners, losers = await count_if_votes_efficient_to_decide_the_result(first_team_won_voters,
                                                                                            second_team_won_voters,
                                                                                            first_team_players,
                                                                                            second_team_players)
        if is_efficient:
            await match_facade.execute_result(ctx, message, losers, winners)


async def count_votes(voting_pool, first_team_players, second_team_players):
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


async def count_if_votes_efficient_to_decide_the_result(left, right, first_team_players, second_team_players):
    all_players = (first_team_players + second_team_players)
    if len(left) >= 0.75 * len(all_players):
        return True, first_team_players, second_team_players
    elif len(right) >= 0.75 * len(all_players):
        return True, second_team_players, first_team_players
    else:
        return False, None, None


async def get_admin_decision(reaction, first_team_players, second_team_players):
    if str(reaction.emoji) == "⬅":
        return first_team_players, second_team_players
    if str(reaction.emoji) == "➡":
        return second_team_players, first_team_players
