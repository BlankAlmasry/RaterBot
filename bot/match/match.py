from bot.match.make_match_validation import validate_teams
import bot.vote as vote

# TODO Refactor
from bot.match.match_factory import create_match


async def make_match(ctx):
    # stage 1, won't persist match creation until it get permitted through votes or admin approval
    error_msg = validate_teams(ctx.message)
    if error_msg:
        await ctx.send(error_msg)
        raise ValueError
    voting_pool = await vote.start_voting(ctx)
    first_team_players, second_team_players = await fetch_first_and_second_team(ctx.message)
    return voting_pool, first_team_players, second_team_players


async def execute_result(ctx, voting_pool, losers, winners):
    # stage 2, Will persist it now
    await voting_pool.delete()
    msg = await create_match(winners, losers, ctx.guild.id, ctx.guild.members)
    await ctx.send(msg)


async def fetch_first_and_second_team(message):
    mentions_len = len(message.mentions) - 1
    team_1 = message.mentions[1: (mentions_len // 2) + 1]
    team_2 = message.mentions[mentions_len // 2 + 1:]
    first_team_players = tuple(map(lambda player: player.name + "#" + player.discriminator, team_1))
    second_team_players = tuple(map(lambda player: player.name + "#" + player.discriminator, team_2))
    return first_team_players, second_team_players
