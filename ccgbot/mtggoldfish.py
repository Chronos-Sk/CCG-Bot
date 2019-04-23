import re

from discord.ext.commands import Context
import requests_async as requests

from ccgbot.decklist import Decklist

MTGGOLDFISH_ROOT = 'https://www.mtggoldfish.com'

async def mtggoldfish_handler(ctx: Context, url: str):
  response = await requests.get(url, verify=False)
  arena_export_match = re.search(r'href=\"(/deck/arena_download/\d+)\"', response.text)
  if not arena_export_match:
    await ctx.author.send('Error finding MTGGoldfish decklist.')
    return
  response_arena = await requests.get(MTGGOLDFISH_ROOT + arena_export_match.group(1), verify=False)
  cards_match = re.search(r'<textarea class=\'copy-paste-box\'>(.+)</textarea>',
                          response_arena.text, re.MULTILINE | re.DOTALL)
  if not cards_match:
    await ctx.author.send('Error parsing MTGGoldfish decklist.')
    return
  cards = cards_match.group(1)
  name_match = re.search(r'<title>(.+) Deck(?: for Magic: the Gathering)?</title>', response.text)
  name = name_match.group(1).strip() if name_match else None
  author_match = re.search(r'<span class=\'deck-view-author\'>by (.+)</span>', response.text)
  author = author_match.group(1) if author_match else None
  thumbnail_match = re.search(
    r'class=\'card-image-tile\' style=\'background-image: url\(.+;(.+)&.+\);\'>', response.text)
  thumbnail = thumbnail_match.group(1) if thumbnail_match else None
  decklist = Decklist(name=name, url=url, author=author, author_url=None, thumbnail=thumbnail)
  decklist.parse_from_mtga(cards)
  return decklist
