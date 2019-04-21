import asyncio

import requests_async as requests
import discord
from discord.ext import commands

from ccgbot import decklist_handlers
from ccgbot import token

from discord.ext.commands.context import Context

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready() -> None:
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def decklist(ctx: Context, url: str) -> None:
  if url.startswith('<') and url.endswith('>'):
    url = url[1:-1]
  handler = decklist_handlers.lookup(url)
  await handler(ctx, url)

if __name__=='__main__':
  bot.run(asyncio.run(token.get()))
