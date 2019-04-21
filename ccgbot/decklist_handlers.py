import re

from ccgbot.decklist import Decklist
from ccgbot.tapped_out import tapped_out_handler

from discord.ext.commands.context import Context
from typing import Awaitable, Callable, Iterable, List, Optional, Pattern, Tuple

DecklistHandler = Callable[[Context, str], Awaitable[Optional[Decklist]]]

def lookup(url: str) -> DecklistHandler:
  return DecklistHandlers.get().lookup(url)

async def _default_handler(ctx: Context, url: str):
  return await ctx.author.send(f"Unknown decklist url: {url}")

class DecklistHandlers:
  @classmethod
  def get(cls) -> 'DecklistHandlers':
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
  ('tappedout.net/mtg-decks/.+', tapped_out_handler),
# ('.*', _default_handler)
)
