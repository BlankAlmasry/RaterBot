from bot.match.match_factory import create_match


async def execute_result(ctx, voting_pool, losers, winners):
    await voting_pool.delete()
    msg = await create_match(winners, losers, ctx.guild.id, ctx.guild.members)
    await ctx.send(msg)


