import re

from ccgbot.decklist import Decklist

import typing
from typing import List, Match, Tuple

def parse_decklist(blob: str, decklist: Decklist) -> None:
  regex = re.compile(r'(\d+) (.+) \(')
  for line in blob.splitlines():
    match = regex.match(line)
    if match:
      decklist.add_card(match.group(2), int(match.group(1)))
