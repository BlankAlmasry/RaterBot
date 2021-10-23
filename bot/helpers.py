from discord.utils import find


async def find_user(name, users):
    return find(lambda n: str(n) == name, users)


async def fetch_user_who_got_mentions_or_message_author(message):
    mentions = message.mentions
    if len(mentions) > 1:  # a user got mentioned
        player = mentions[1]
    else:
        player = message.author
    return player
