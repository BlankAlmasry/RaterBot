from bot.match.match import make_match
from bot.match.match_factory import create_match
from bot.match.match_voting_handler import match_voting_pool_handler


async def start_match(ctx):
    voting_pool, first_team_players, second_team_players = await make_match(ctx)
    return voting_pool, first_team_players, second_team_players


async def start_match_voting(message, first_team_players, second_team_players,
                             ctx, reaction, user):
    await match_voting_pool_handler(message, first_team_players, second_team_players,
                                    ctx, reaction, user)


async def execute_result(ctx, voting_pool, losers, winners):
    await voting_pool.delete()
    msg = await create_match(winners, losers, ctx.guild.id, ctx.guild.members)
    await ctx.send(msg)
