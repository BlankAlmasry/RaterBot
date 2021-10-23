from collections import namedtuple

from bot.raterapi_requests import create_match_request
from bot.responses import create_match_response


async def create_match(winners, losers, guild_id, users):
    match = await match_factory(winners, losers)
    res = await create_match_request(guild_id, match._asdict())
    match_response = await create_match_response(res, users)
    return match_response


async def match_factory(winners, losers) -> namedtuple:
    Match = namedtuple("Match", "teams")
    match_data = Match([
        {"users": winners, "result": 1},
        {"users": losers, "result": 0}
    ])
    return match_data
