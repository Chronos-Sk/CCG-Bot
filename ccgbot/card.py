import functools

from typing import List, NamedTuple

class Card(NamedTuple):
  name: str
  types: List[str]
  colors: List[str]
  cmc: int
  cost: str

  @classmethod
  @functools.lru_cache(maxsize=512)
  def lookup(cls, card_name: str) -> 'Card':
    return cls(card_name, None, None, None, None)
