from collections import namedtuple
from bot.match.make_match_validation import validate_teams
from bot.responses import create_match_response
from bot.raterapi_requests import create_match_request
import bot.vote as vote


# TODO Refactor


async def make_match(ctx):
    error_msg = validate_teams(ctx.message)
    if error_msg:
        await ctx.send(error_msg)
        raise ValueError
    message = await vote.start_voting(ctx)
    first_team_players, second_team_players = await fetch_first_and_second_team(ctx)
    return message, first_team_players, second_team_players


async def create_match(winners, losers, guild_id, users):
    new_match = await match_factory(winners, losers)
    res = await create_match_request(guild_id, new_match)
    msg = await create_match_response(res, users)
    return msg


async def match_factory(winners, losers):
    Match = namedtuple("Match", "teams")
    match_data = Match([
        {"users": winners, "result": 1},
        {"users": losers, "result": 0}
    ])
    return match_data._asdict()


async def match_voting_pool_handler(message, first_team_players, second_team_players,
                                    ctx, reaction, user):
    # Match module have control over Vote module
    await vote.vote(message, first_team_players, second_team_players,
                    ctx, reaction, user)


async def fetch_first_and_second_team(ctx):
    mentions_len = len(ctx.message.mentions) - 1
    team_1 = ctx.message.mentions[1: (mentions_len // 2) + 1]
    team_2 = ctx.message.mentions[mentions_len // 2 + 1:]
    first_team_players = tuple(map(lambda player: player.name + "#" + player.discriminator, team_1))
    second_team_players = tuple(map(lambda player: player.name + "#" + player.discriminator, team_2))
    return first_team_players, second_team_players


async def execute_result(ctx, message, losers, winners):
    await message.delete()
    msg = await create_match(winners, losers, ctx.guild.id, ctx.guild.members)
    await ctx.send(msg)
