from collections import defaultdict
import re

from discord.embeds import Embed
from typing import DefaultDict, List, Optional, Tuple, Union

from ccgbot.card import Card

class Decklist:
  def __init__(self,
               name: str,
               url: Optional[str] = None,
               author: Optional[str] = None,
               author_url: Optional[str] = None,
               thumbnail: Optional[str] = None):
    self._name = name
    self._url = url
    self._author = author
    self._author_url = author_url
    self._thumbnail = thumbnail
    self._cards = defaultdict(int)
  
  def add_card(self, card: Union[str, Card], count: int = 1) -> None:
    if isinstance(card, str):
      card = Card.lookup(card)
    self._cards[card] += count

  def parse_from_mtga(self, text: str) -> None:
    regex = re.compile(r'(\d+) (.+) \(')
    for line in text.splitlines():
      match = regex.match(line)
      if match:
        self.add_card(match.group(2), int(match.group(1)))

  def _sorted_cards(self) -> List[Tuple[Card, int]]:
    return sorted(self._cards.items())

  def to_embed(self) -> Embed:
    body = '\n'.join(f'{num} {card.name}' for card, num in self._sorted_cards())
    embed = Embed(title=self.name, url=self.url, description=body)
    embed.set_author(name=self.author, url=self.author_url)
    embed.set_thumbnail(url=self.thumbnail)
    return embed

  @property
  def name(self):
    return self._name

  @property
  def author(self):
    return self._author

  @property
  def author_url(self):
    return self._author_url

  @property
  def url(self):
    return self._url

  @property
  def thumbnail(self):
    return self._thumbnail

  _name: str
  _url: Optional[str]
  _author: Optional[str]
  _author_url: Optional[str]
  _thumbnail: Optional[str]
  _cards: DefaultDict[Card, int]
