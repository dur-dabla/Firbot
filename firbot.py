#!/usr/bin/env python 
#-*- coding: utf-8 -*-

import asyncio
import os
import traceback
from pathlib import Path

import discord
from crontab import CronTab

client = discord.Client()
running_tasks = []

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

client.run(os.environ['FIRBOT_TOKEN'])
