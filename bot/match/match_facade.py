from bot.match.match import make_match
from bot.match.match_factory import match_factory
from bot.match.match_voting_handler import match_voting_pool_handler


async def start_match(ctx):
    voting_pool, first_team_players, second_team_players = await make_match(ctx)
    return voting_pool, first_team_players, second_team_players


async def add_vote(message, first_team_players, second_team_players,
                   ctx, reaction, user):
    await match_voting_pool_handler(message, first_team_players, second_team_players,
                                    ctx, reaction, user)


async def execute_result(ctx, voting_pool, losers, winners):
    await voting_pool.delete()
    msg = await match_factory(winners, losers, ctx.guild.id, ctx.guild.members)
    await ctx.send(msg)

