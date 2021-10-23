from bot.leaderboard.leaderboard_factory import leaderboard_factory


async def try_paginate_leaderboard(ctx, reaction, message, page):
    if str(reaction.emoji) == "⬅":
        await message.edit(content=await leaderboard_factory(ctx.guild.id, ctx.message.author, page - 1))
    if str(reaction.emoji) == "➡":
        await message.edit(content=await leaderboard_factory(ctx.guild.id, ctx.message.author, page + 1))
