import pprint
import re

from absl import flags
from absl import logging
from discord import Guild, Emoji, Client
from typing import Pattern, Tuple

SPLIT_COST_REGEX = re.compile(r'\{(.)/(.)\}')

FLAGS = flags.FLAGS
flags.DEFINE_integer('manamoji_guild_id', 569725225214803979,
                     'Discord guild/server hosting the emoji')

def substitute(text: str) -> str:
  return ManamojiDb.get().substitute(text)

class ManamojiDb:
  @classmethod
  def get(cls) -> 'ManamojiDb':
    if not hasattr(cls, 'INSTANCE'):
      cls.INSTANCE = cls()
    return cls.INSTANCE
  
  def __init__(self):
    self._initialized = False
    self._mappings = {}
  
  async def initialize(self, client: Client) -> None:
    guild = client.get_guild(FLAGS.manamoji_guild_id)
    emojis = await guild.fetch_emojis()
    manamojis = [emoji for emoji in emojis if emoji.name.startswith('mana')]
    logging.info('Found %s manamojis.', len(manamojis))
    logging.vlog(1, 'Emojis found: %s', manamojis)
    mappings = []
    for manamoji in manamojis:
      pattern = '{' + manamoji.name[4:] + '}'
      mappings.append((pattern, manamoji))
      upper_pattern = pattern.upper()
      if upper_pattern != pattern:
        mappings.append((upper_pattern, manamoji))
    self._mappings = tuple(mappings)
    if logging.vlog_is_on(1):
      logging.vlog(1, 'Emoji mappings: %s', pprint.pformat(self._mappings))
    self._initialized = True
  
  def substitute(self, text: str) -> str:
    assert self._initialized
    text = SPLIT_COST_REGEX.sub(r'{\1\2}', text)
    for pattern, emoji in self._mappings:
      text = text.replace(pattern, str(emoji))
    return text

  _initialized: bool
  _mappings: Tuple[Tuple[str, Emoji], ...]
