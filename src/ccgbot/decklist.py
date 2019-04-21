from collections import defaultdict

from typing import DefaultDict, List, Optional, Tuple

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
  
  def add_card(self, name: str, count: int = 1) -> None:
    self._cards[name] += count

  def sorted_cards(self) -> List[Tuple[str, int]]:
    return sorted(self._cards.items())

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
  _cards: DefaultDict[str, int]
