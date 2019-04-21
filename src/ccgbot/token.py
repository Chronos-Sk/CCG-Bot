import os.path

import requests_async as requests

TOKEN_FILE = './token.txt'

# Currently just uses the custom project GCS Metadata value for `discord_token`.
METADATA_URL = 'http://metadata.google.internal/computeMetadata/v1/project/'
TOKEN_ATTRIBUTE_NAME = 'attributes/discord_token'

async def get() -> str:
  if os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE, 'r') as fin:
      return fin.read()
  return await lookup_metadata(TOKEN_ATTRIBUTE_NAME, timeout=60)

async def lookup_metadata(attribute_name: str, **kwargs) -> str:
  request = await requests.get(
    METADATA_URL + attribute_name,
    headers={'Metadata-Flavor': 'Google'},
    **kwargs)
  return request.text
