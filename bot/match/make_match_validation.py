def validate_teams(message):
    if len(message.mentions) == 1:
        # only the bot got mentions
        return "mentions the players and separate between them with `vs` according to their tea,"

    if len(message.mentions) == 2:
        # only 1 player
        return "mention both opponent in same line please, and separate them with `vs` "

    if "vs" not in message.content:
        return "separate the 2 teams with `vs` in between"

    # Lazy validation, would fix an early `vs` or a late one by auto-balancing teams
    if (len(message.mentions) - 1) % 2 != 0:
        return "uneven teams"

