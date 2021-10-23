from bot.helpers import fetch_user_who_got_mentions_or_message_author
from bot.stats.stats_factory import stats_factory


async def get_stats(ctx):
    player = await fetch_user_who_got_mentions_or_message_author(ctx.message)
    msg = await stats_factory(player, ctx.guild.id)
    await ctx.send(msg)


