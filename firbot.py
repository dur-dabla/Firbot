#!/usr/bin/env python 
#-*- coding: utf-8 -*-

import re
import random
import asyncio
import os
import traceback
from pathlib import Path

import sqlite3

import discord
from discord.ext import commands
from crontab import CronTab

from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot.trainers import ListTrainer

BOT_PREFIX = ('?', '!')
client = commands.Bot(command_prefix=BOT_PREFIX)

running_tasks = []

noob = False
if not os.path.isfile("db.sqlite3"):
    noob = True

chatbot = ChatBot('Firbot')

if noob:
    trainer = ChatterBotCorpusTrainer(chatbot)
    trainer.train("chatterbot.corpus.french")

trainer = ListTrainer(chatbot)

async def send_message(interval, channel, text):
    await client.wait_until_ready()
    cron = CronTab(interval)
    while True:
        await asyncio.sleep(cron.next())
        try:
            await channel.send(text)
        except asyncio.CancelledError:
            print(f"Cancelling task with interval {interval}")
            raise
        except Exception:
            print(f"Could not send `{text}` to `{channel}:`")
            traceback.format_exc()

@client.event
async def on_ready():
    # Cancel running tasks if any
    for task in running_tasks:
        task.cancel()
    del running_tasks[:]

    try:
        # Read data from the configuration file
        cron_file = Path(__file__).parent / 'cron.tab'
        with cron_file.open() as fd:
            lines = fd.read()
    except Exception:
        print("Failed to read the configuration file")
        traceback.format_exc()
        raise

    for line in lines.split('\n'):
        line = line.strip()

        # Ignore blank lines and comments
        if not line or line.startswith('#'):
            continue

        # Schedule tasks for valid lines
        try:
            interval, channel, text = line.split(',', 2)

            await client.wait_until_ready()
            channel = client.get_channel(int(channel.strip()))
            print(f"Found channel: {channel.name}, {channel.id}")
            text = text.strip()

            print(f'Scheduling `{text}` with schedule `{interval.strip()}`')
            task = client.loop.create_task(send_message(interval, channel, text))
            running_tasks.append(task)
        except Exception as err:
            print('Could not schedule task:')
            traceback.format_exc()
            raise

@client.command(pass_context=True)
async def learn(ctx, *args):
    print(f"Handle learn command: {args}")
    trainer.train(args)

@client.event
@asyncio.coroutine
def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    print(f"Received: '{message.content}'")
    if message.content.startswith(BOT_PREFIX):
        # Pass on to rest of the client commands
        print("Process command")
        yield from client.process_commands(message)
    else:
        if client.user.id in list(map(lambda m: m.id, message.mentions)):
            cleanedMsg = re.sub('<@.*?>', '', message.content).strip()
            answer = chatbot.get_response(cleanedMsg)
            yield from message.channel.trigger_typing()
            yield from asyncio.sleep(random.randint(1,3))
            yield from message.channel.send(answer)

client.run(os.environ['FIRBOT_TOKEN'])
