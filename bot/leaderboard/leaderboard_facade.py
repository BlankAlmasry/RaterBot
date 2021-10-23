from bot.leaderboard.leaderboard import get_leaderboard
from bot.leaderboard.paginate_leaderboard import paginate_leaderboard


async def print_leaderboard(ctx):
    return await get_leaderboard(ctx)


async def try_paginate_leaderboard(ctx, reaction, leaderboard_message, current_page):
    await paginate_leaderboard(ctx, reaction, leaderboard_message, current_page)
