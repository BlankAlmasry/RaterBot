from bot.helpers import find_user


# ALL RESPONSES was created with a series of trial and error, was the sole purpose of it looking good on discord
async def create_player_stat_response(player, player_rank):
    msg = f"`Rank: {player['rank']['rank']}`\n" \
          f"`Rating: {int(player['rating'])}{'?' if player_rank['rank']['rank'] is None else ''}`\n" \
          f"`Win/Loses: {player['wins']}/{player['loses']}`\n" \
          f"`Win Ratio: {round((player['wins'] / (player['loses'] + player['wins'])) * 100, 2)}%`\n"
    return msg


async def create_get_rank_response(player_rank):
    response = ""
    if not player_rank['rank']['rank'] is None:
        response = f"`Leaderboard: {player_rank['rank']['rank']}th Over {player_rank['rank']['all']} players`"
    else:
        response = "`Leaderboard: not enough games yet`"
    return response


async def create_leaderboard_response(author, leaderboard, rank):
    header = "`     #Name       #Rank              #Rating \n"
    body = ""
    for index, user in enumerate(leaderboard["data"]):
        index = index + (leaderboard['meta']['current_page'] - 1) * 10
        user_msg = f" #{index + 1}{' ' * (4 - len(str(index + 1)))}" + \
                   f"{user['name'].split('#')[0]}{' ' * (12 - len(user['name'].split('#')[0]))}" \
                   f"{user['rank']['rank']}{' ' * (19 - len(user['rank']['rank']))}" \
                   f"{round(user['rating'])}   \n"
        body += user_msg
    footer_last_line = (13 - len(author.name)
                        - len(str(leaderboard['meta']['current_page'])) -
                        len(str(leaderboard['meta']['current_page'])))
    footer = f"   Page {leaderboard['meta']['current_page']}" \
             f" of {leaderboard['meta']['last_page']} •" \
             f" Your Rank: {rank if rank is not None else '?'} •  {author.name}" \
             f"{' ' * footer_last_line}`"
    return header + body + footer


async def create_match_response(data, users):
    msg = "**New Ratings**\n"
    for user in data["users"]:
        user_mention = await find_user(user["name"], users)
        msg += f"{user_mention.mention}" + "\n" + "`Rank : " + user["rank"][
            "rank"] + " " + str(round(user["rank"]["points"])) + " LP" + "\n" + "Rating : " + str(
            round(user["rating"])) + "`\n"
    return msg
