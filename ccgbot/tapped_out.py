import re

from discord.ext.commands.context import Context
import requests_async as requests

from ccgbot.decklist import Decklist

async def tapped_out_handler(ctx: Context, url: str):
  response = await requests.get(url, verify=False)
  name_match = re.search(r'<title>(.+)</title>', response.text)
  author_match = re.search(r'<p class=\"subtitle\">by <a href=\'(/users/(.+)/)\'>', response.text)
  thumbnail_match = re.search('<img class=\"featured-card\" src=\"(.+)\" />', response.text)
  cards_match = re.search(r'<textarea id=\"mtga-textarea\">(.+)</textarea>',
                          response.text, re.MULTILINE | re.DOTALL)
  name = name_match.group(1) if name_match else None
  if author_match:
    author = author_match.group(2)
    author_url = 'http://tappedout.net' + author_match.group(1)
  else:
    author = None
    author_url = None
  thumbnail = 'http:' + thumbnail_match.group(1) if thumbnail_match else None
  if not cards_match:
    await ctx.author.send(f'Error parsing Tapped Out decklist.')
    return
  cards = cards_match.group(1)
  decklist = Decklist(name=name, url=url, author=author, author_url=author_url, thumbnail=thumbnail)
  decklist.parse_from_mtga(cards)
  return decklist
