from bot.raterapi_requests import get_leaderboard_request, get_user_rank_request
from bot.responses import create_leaderboard_response


async def leaderboard_factory(guild_id, author, page=1):
    # in case user asked for previous page when his is on the first page
    if page < 1:
        page = 1
    response = await get_leaderboard_request(guild_id, page)

    # validate page exist
    if not response["data"]:
        return None

    rank_on_server = (await get_user_rank_request(guild_id, author))["rank"]["rank"]
    return await create_leaderboard_response(author, response, rank_on_server)
