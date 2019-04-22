import asyncio
import pprint

from absl import app
from absl import logging
import discord
from discord.ext import commands
from discord.ext.commands.context import Context
import requests_async as requests

from ccgbot import decklist_handlers
from ccgbot import token
from ccgbot.carddb import CardDb
from ccgbot.manamojidb import ManamojiDb

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready() -> None:
  logging.info('Logged in as %s (%s)', bot.user.name, bot.user.id)
  await ManamojiDb.get().initialize(bot)

@bot.command()
async def decklist(ctx: Context, url: str, mode: str = 'compact') -> None:
  if url.startswith('<') and url.endswith('>'):
    url = url[1:-1]
  logging.info('Looking up decklist for: %s', url)
  handler = decklist_handlers.lookup(url)
  decklist = await handler(ctx, url)
  if decklist:
    logging.info('Found decklist named: %s', decklist.name)
    if logging.vlog_is_on(1):
      logging.vlog(1, 'Decklist contents: %s', pprint.pformat(decklist.to_embed().to_dict()))
    await ctx.send(embed=decklist.to_embed(mode == 'flat'))
  else:
    logging.info('No decklist found for: %s', url)

async def setUp() -> str:
  discord_token, _, = await asyncio.gather(token.get(), CardDb.get().initialize())
  return discord_token

def main(argv):
  if len(argv) > 1: logging.fatal('Unexpected nonflag arguments: %s', argv)
  discord_token = asyncio.run(setUp())
  bot.run(discord_token)

if __name__=='__main__':
  app.run(main)
