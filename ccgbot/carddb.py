import asyncio
import functools
import json

from absl import flags
from absl import logging
from aiohttp import ClientResponseError
from gcloud.aio.storage import Storage, Bucket
import requests_async as requests
import typing
from typing import Awaitable, Dict, NamedTuple, Optional, Tuple

CARDDB_BUCKET = 'discord-ccg-bot.appspot.com'
CARDDB_DB_FILE = 'AllCards.json'

FLAGS = flags.FLAGS
flags.DEFINE_string('carddb_local_file', None, 'Forces loading from a local json file.')

class Card(NamedTuple):
  name: str
  types: Tuple[str, ...]
  colors: Tuple[str, ...]
  cmc: int
  cost: str

  @staticmethod
  def lookup(card_name: str) -> Optional['Card']:
    return CardDb.get().lookup(card_name)
  
  @classmethod
  def unknown(cls) -> 'Card':
    return UNKNOWN_CARD

UNKNOWN_CARD = Card('Unknown', tuple(), tuple(), 0, '')

class CardDb:
  @classmethod
  def get(cls) -> 'CardDb':
    if not hasattr(cls, 'INSTANCE'):
      cls.INSTANCE = cls()
    return cls.INSTANCE

  def __init__(self):
    self._database = {}
    self._is_initialized = asyncio.Event()

  async def initialize(self) -> None:
    logging.vlog(1, 'Initializing CardDb.')
    if FLAGS.carddb_local_file:
      logging.info('Initializing CardDb from local file: %s', FLAGS.carddb_local_file)
      with open(FLAGS.carddb_local_file, 'r') as fin:
        db_json = fin.read()
    else:
      logging.info('Initializing CardDb from cloud file: %s/%s', CARDDB_BUCKET, CARDDB_DB_FILE)
      storage = Storage()
      bucket = storage.get_bucket(CARDDB_BUCKET)
      blob = await bucket.get_blob(CARDDB_DB_FILE)
      db_json = await blob.download()
      logging.info('Loaded cloud file.')
    await self._parse_db_json(db_json)
    self._is_initialized.set()

  async def _parse_db_json(self, json_blob: str) -> None:
    raw_card_dict = json.loads(json_blob)
    for name, card_dict in raw_card_dict.items():
      card = Card(card_dict['name'], tuple(card_dict['types']), tuple(card_dict['colors']),
                  card_dict['convertedManaCost'], card_dict.get('manaCost', ''))
      logging.vlog(2, 'Creating card: %s', card)
      self._database[name] = card
      names = card_dict.get('names', [])
      if len(names) == 2 and names[0] == name:
        other_card_dict = raw_card_dict[names[1]]
        double_name = ' // '.join(names)
        other_mana_cost = other_card_dict.get('manaCost', '')
        double_cost = f'{card.cost}/{other_mana_cost}' if other_mana_cost else card.cost
        double_card = Card(double_name, card.types + tuple(other_card_dict['types']), card.colors,
                           card.cmc, double_cost)
        logging.vlog(2, 'Creating double-card: %s', double_card)
        self._database[double_name] = double_card

  def lookup(self, card_name: str) -> Optional[Card]:
    assert self._is_initialized.is_set()
    return self._database.get(card_name, None)

  async def wait_for_initialized(self):
    await typing.cast(Awaitable, self._is_initialized.wait())

  _database: Dict[str, Card]
  _is_initialized: asyncio.Event
