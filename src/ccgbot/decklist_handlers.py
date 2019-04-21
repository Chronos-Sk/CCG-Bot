import re

import requests_async as requests

from ccgbot import mtga
from ccgbot.decklist import Decklist

from discord.embeds import Embed
from discord.ext.commands.context import Context
from typing import Awaitable, Callable, Iterable, List, Pattern, Tuple

DecklistHandler = Callable[[Context, str], Awaitable[None]]

def lookup(url: str) -> DecklistHandler:
  return DecklistSites.get().lookup(url)

async def post_deck(ctx: Context, decklist: Decklist) -> None:
  cards = '\n'.join(f'{num} {name}' for name, num in decklist.sorted_cards())
  embed = Embed(title=decklist.name, url=decklist.url, description=cards)
  embed.set_author(name=decklist.author, url=decklist.author_url)
  embed.set_thumbnail(url=decklist.thumbnail)
  print(embed.to_dict())
  await ctx.send(embed=embed)

### Handlers ###

# Pytype has problems if handlers are defined with an explicit return type.
async def _tapped_out_handler(ctx: Context, url: str):
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
    return await ctx.author.send(f"Error parsing Tapped Out decklist.")
  cards = cards_match.group(1)
  decklist = Decklist(name=name, url=url, author=author, author_url=author_url, thumbnail=thumbnail)
  mtga.parse_decklist(cards, decklist)
  await post_deck(ctx, decklist)

async def _default_handler(ctx: Context, url: str):
  await ctx.author.send(f"Unknown decklist url: {url}")

### End Handlers ###

class DecklistSites:
  @classmethod
  def get(cls) -> 'DecklistSites':
    if not hasattr(cls, 'INSTANCE'):
      cls.INSTANCE = cls(DECKLIST_SITES)
    return cls.INSTANCE
  
  def __init__(self, decklist_sites: Tuple[Tuple[str, DecklistHandler], ...]):
    handlers = []
    for pattern, handler in decklist_sites:
      regex = re.compile(f'https?://{pattern}')
      handlers.append((regex, handler))
    self._handlers = tuple(handlers)
  
  def lookup(self, url: str) -> DecklistHandler:
    for regex, handler in self._handlers:
      if regex.match(url):
        return handler
    return _default_handler

  _handlers: Tuple[Tuple[Pattern, DecklistHandler], ...]

DECKLIST_SITES = (
  ('tappedout.net/mtg-decks/.+', _tapped_out_handler),
# ('.*', _default_handler)
)
