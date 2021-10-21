from command_responses import create_player_stat_response, create_get_rank_response
from raterapi_requests import get_user_stats_request, get_user_rank_request


async def get_player_stats(player, guild_id):
    player_stats = await get_user_stats_request(guild_id, player)
    player_rank = await get_user_rank_request(guild_id, player)

    user_stats_message = await create_player_stat_response(player_stats, player_rank)
    user_rank_message = await create_get_rank_response(player_rank)

    return user_stats_message + user_rank_message

