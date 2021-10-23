import bot.vote as vote


async def match_voting_pool_handler(message, first_team_players, second_team_players,
                                    ctx, reaction, user):
    # Match module have control over Vote module
    await vote.vote(message, first_team_players, second_team_players,
                    ctx, reaction, user)
