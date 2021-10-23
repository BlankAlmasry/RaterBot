from bot.responses import create_leaderboard_response
from bot.raterapi_requests import get_leaderboard_request, get_user_rank_request


async def print_leaderboard(ctx):
    current_page = 1
    message = None
    leaderboard_response = await get_leaderboard(ctx.guild.id, ctx.message.author)
    if leaderboard_response is None:
        await ctx.send("not enough games played in the server yet")
    else:
        message = await ctx.send(leaderboard_response)
        await message.add_reaction("⬅")
        await message.add_reaction("➡")
    return current_page, message


async def try_paginate_leaderboard(ctx, reaction, message, page):
    if str(reaction.emoji) == "⬅":
        await message.edit(content=await get_leaderboard(ctx.guild.id, ctx.message.author, page - 1))
    if str(reaction.emoji) == "➡":
        await message.edit(content=await get_leaderboard(ctx.guild.id, ctx.message.author, page + 1))


async def get_leaderboard(guild_id, author, page=1):
    if page < 1:  # in case user asked for previous page when his is on the first page
        page = 1
    response = await get_leaderboard_request(guild_id, page)
    # validate page exist
    if not response["data"]:
        return None
    rank_on_server = (await get_user_rank_request(guild_id, author))["rank"]["rank"]
    return await create_leaderboard_response(author, response, rank_on_server)
