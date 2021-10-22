from responses import create_leaderboard_response
from raterapi_requests import get_leaderboard_request, get_user_rank_request


async def get_rankings(ctx):
    page = 1
    message = None
    leaderboard = await get_leaderboard(ctx.guild.id, ctx.message.author)
    if leaderboard is None:
        await ctx.send("not enough games played in the server yet")
    else:
        message = await ctx.send(leaderboard)
        await message.add_reaction("⬅")
        await message.add_reaction("➡")
    return page, message


async def paginate_rankings(ctx, reaction, message, page):
    if str(reaction.emoji) == "⬅":
        await message.edit(content=await get_leaderboard(ctx.guild.id, ctx.message.author, page - 1))
    if str(reaction.emoji) == "➡":
        await message.edit(content=await get_leaderboard(ctx.guild.id, ctx.message.author, page + 1))


async def get_leaderboard(guild_id, author, page=1):
    if page < 1:  # in case user asked for previous page when his is on the first page
        page = 1
    leaderboard = await get_leaderboard_request(guild_id, page)
    # validate page exist
    if not leaderboard["data"]:
        return None
    rank_on_server = (await get_user_rank_request(guild_id, author))["rank"]["rank"]
    return await create_leaderboard_response(author, leaderboard, rank_on_server)
