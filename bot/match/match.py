from bot.match.helpers import fetch_first_and_second_team
from bot.match.make_match_validation import validate_teams
import bot.match.vote.vote as vote


async def make_match(ctx):
    # stage 1, won't persist match creation until it get permitted through votes or admin approval
    # Vote module should delegate to match_facade for actual creation once result is known
    error_msg = validate_teams(ctx.message)
    if error_msg:
        await ctx.send(error_msg)
        raise ValueError
    voting_pool = await vote.start_voting_pool(ctx)
    first_team_players, second_team_players = await fetch_first_and_second_team(ctx.message)
    return voting_pool, first_team_players, second_team_players


