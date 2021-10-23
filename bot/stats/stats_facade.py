from bot.stats.stats import get_stats


async def print_stats(ctx):
    await get_stats(ctx)
