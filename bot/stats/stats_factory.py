from bot.raterapi_requests import get_user_stats_request, get_user_rank_request
from bot.responses import create_player_stat_response, create_get_rank_response


async def stats_factory(player, guild_id):
    player_stats = await get_user_stats_request(guild_id, player)
    player_rank = await get_user_rank_request(guild_id, player)

    user_stats_message = await create_player_stat_response(player_stats, player_rank)
    user_rank_message = await create_get_rank_response(player_rank)

    return user_stats_message + user_rank_message
