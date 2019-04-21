import os.path

from absl import flags
from absl import logging
import requests_async as requests

DEFAULT_TOKEN_URL = 'http://metadata.google.internal/computeMetadata/v1/project/attributes/discord_token'

FLAGS = flags.FLAGS
flags.DEFINE_string('discord_token_file', './token.txt', 'File to retrieve bot token from.')
flags.DEFINE_string('discord_token_url', DEFAULT_TOKEN_URL, 'URL to retrieve bot token from.')

async def get() -> str:
  if os.path.exists(FLAGS.discord_token_file):
    logging.info('Reading token from file: %s', FLAGS.discord_token_file)
    with open(FLAGS.discord_token_file, 'r') as fin:
      return fin.read()
  logging.info('Reading token from ')
  request = await requests.get(
    FLAGS.discord_token_url,
    headers={'Metadata-Flavor': 'Google'},
    timeout=60)
  return request.text
