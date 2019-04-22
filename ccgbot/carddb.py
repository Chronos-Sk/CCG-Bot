import asyncio
import functools
import json

from absl import flags
from absl import logging
from aiohttp import ClientResponseError
import aiosqlite
from gcloud.aio.storage import Storage, Bucket
import requests_async as requests
import typing
from typing import Awaitable, Dict, NamedTuple, Optional, Tuple

REMOTE_DB_URL = 'https://mtgjson.com/json/AllCards.json'
VERSION_URL = 'https://mtgjson.com/json/version.json'
CARDDB_BUCKET = 'discord-ccg-bot.appspot.com'
CARDDB_DB_FILE = 'carddb.json'
CARDDB_VERSION_FILE = 'carddb.version.json'

FLAGS = flags.FLAGS
flags.DEFINE_string('carddb_local_file', None, 'Forces loading from a local sqlite file.')

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
    self._initialized = False

  async def initialize(self) -> None:
    logging.vlog(1, 'Initializing CardDb.')
    if FLAGS.carddb_local_file:
      logging.info('Initializing CardDb from local file: %s', FLAGS.carddb_local_file)
      with open(FLAGS.carddb_local_file, 'r') as fin:
        db_json = fin.read()
    else:
      storage = Storage()
      bucket = storage.get_bucket(CARDDB_BUCKET)
      try:
        current_version_json = await bucket.get_blob(CARDDB_VERSION_FILE).download()
      except ClientResponseError as ex:
        logging.error('Could not load CardDb current version from cloud repo: %s', ex)
        current_version = 'unknown'
      else:
        current_version = json.loads(current_version_json)['version']
        logging.vlog(1, 'CardDb current database version: %s', current_version)
      remote_version_json = await requests.get(VERSION_URL)
      remote_version = json.loads(remote_version_json)['version']
      logging.vlog(1, 'CardDb remote database version: %s', remote_version)
      version_mismatch = current_version != remote_version
      if version_mismatch:
        logging.info('CardDb version mismatch (%s != %s). Loading from remote.',
                     current_version, remote_version)
        db_json = await self._fetch_remote_database()
        await bucket.get_blob(CARDDB_VERSION_FILE).upload(remote_version_json)
      else:
        logging.vlog(1, 'Loading CardDb from cloud storage.')
        db_json = await self._fetch_cloud_database(bucket)
    await self._parse_db_json(db_json)
    self._initialized = True

  @staticmethod
  async def _fetch_cloud_database(bucket: Bucket) -> str:
    return await bucket.get_blob(CARDDB_DB_FILE).download()

  @staticmethod
  async def _fetch_remote_database() -> str:
    response = await requests.get(REMOTE_DB_URL, timeout=60)
    return response.text

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
    assert self._initialized
    return self._database.get(card_name, None)

  _database: Dict[str, Card]
  _initialized: bool
