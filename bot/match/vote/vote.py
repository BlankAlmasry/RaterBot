import bot.match.match_facade as match_facade
from bot.match.vote.helpers import get_admin_decision, count_votes, count_if_votes_efficient_to_decide_the_result


async def start_voting_pool(ctx):
    message = await ctx.send('Which team won?')
    await message.add_reaction("⬅")
    await message.add_reaction("➡")
    return message


# once started
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
        # is_efficient if 75% of the players choose the same winner
        if is_efficient:
            await match_facade.execute_result(ctx, message, losers, winners)
