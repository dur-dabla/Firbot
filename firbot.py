#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import asyncio
import importlib.resources
import os
import traceback

import discord.ext.commands
from crontab import CronTab

import firbot.data
from firbot.cherchord import run_cherchord

bot = discord.ext.commands.Bot(command_prefix='!')
running_tasks = []


async def send_message(interval, channel, text):
    await bot.wait_until_ready()
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


@bot.event
async def on_ready():
    # Cancel running tasks if any
    for task in running_tasks:
        task.cancel()
    del running_tasks[:]

    try:
        # Read data from the configuration file
        cron_lines = importlib.resources.read_text(firbot.data, 'cron.tab')
    except Exception:
        print("Failed to read the configuration file")
        traceback.format_exc()
        raise

    for line in cron_lines.split('\n'):
        line = line.strip()

        # Ignore blank lines and comments
        if not line or line.startswith('#'):
            continue

        # Schedule tasks for valid lines
        try:
            interval, channel, text = line.split(',', 2)

            await bot.wait_until_ready()
            channel = bot.get_channel(int(channel.strip()))
            print(f"Found channel: {channel.name}, {channel.id}")
            text = text.strip()

            print(f'Scheduling `{text}` with schedule `{interval.strip()}`')
            task = bot.loop.create_task(send_message(interval, channel, text))
            running_tasks.append(task)
        except Exception:
            print('Could not schedule task:')
            traceback.format_exc()
            raise


@bot.command()
async def cherchord(context, *args):
    for line in run_cherchord(*args):
        await context.send(line)


bot.run(os.environ['FIRBOT_TOKEN'])
