from collections import defaultdict
import re

from absl import logging
from discord.embeds import Embed
import typing
from typing import DefaultDict, List, Optional, Tuple, Union

from ccgbot import manamojidb
from ccgbot.carddb import Card

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
      card_obj = Card.lookup(card)
    else:
      card_obj = card
    if not card:
      logging.info('Unknown card: %s', card)
      card_obj = Card.unknown()
    self._cards[typing.cast(Card, card_obj)] += count

  def parse_from_mtga(self, text: str) -> None:
    regex = re.compile(r'(\d+) (.+) \(')
    for line in text.splitlines():
      match = regex.match(line)
      if match:
        self.add_card(match.group(2), int(match.group(1)))

  def _sorted_cards(self) -> List[Tuple[Card, int]]:
    return sorted(self._cards.items())

  def _get_cards_by_type(self):
    cards_by_type = defaultdict(list)
    for card, count in self._cards.items():
      cards_by_type[card.types[0]].append((card, count))
    for _, cards in cards_by_type.items():
      cards.sort()
    return cards_by_type

  def to_embed(self, flat: bool = False) -> Embed:
    #body = '\n'.join(f'{num} {card.name} {card.cost}' for card, num in self._sorted_cards())
    #body = manamojidb.substitute(body)
    embed = Embed(title=self.name, url=self.url)
    embed.set_author(name=self.author, url=self.author_url)
    embed.set_thumbnail(url=self.thumbnail)
    cards_by_type = self._get_cards_by_type()
    for type_ in ['Land', 'Creature', 'Sorcery', 'Instant',
                  'Artifact', 'Enchantment', 'Plainswalker']:
      cards_body = '\n'.join(f'{num} {card.name}' + (f'   {card.cost}' if flat else '')
                             for card, num in cards_by_type.get(type_, []))
      if not cards_body:
        continue
      cards_body = manamojidb.substitute(cards_body)
      embed.add_field(name=type_, value=cards_body, inline=not flat)
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
