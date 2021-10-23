async def fetch_first_and_second_team(message):
    mentions_len = len(message.mentions) - 1
    team_1 = message.mentions[1: (mentions_len // 2) + 1]
    team_2 = message.mentions[mentions_len // 2 + 1:]
    first_team_players = tuple(map(lambda player: player.name + "#" + player.discriminator, team_1))
    second_team_players = tuple(map(lambda player: player.name + "#" + player.discriminator, team_2))
    return first_team_players, second_team_players
