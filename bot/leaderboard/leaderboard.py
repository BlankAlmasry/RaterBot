from bot.leaderboard.leaderboard_factory import leaderboard_factory


async def get_leaderboard(ctx):
    current_page = 1
    message = None
    leaderboard_response = await leaderboard_factory(ctx.guild.id, ctx.message.author)
    if leaderboard_response is None:
        await ctx.send("not enough games played in the server yet")
    else:
        message = await ctx.send(leaderboard_response)
        await message.add_reaction("⬅")
        await message.add_reaction("➡")
    return current_page, message
