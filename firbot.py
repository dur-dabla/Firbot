#!/usr/bin/env python 
#-*- coding: utf-8 -*-

import asyncio
import os
import traceback
from pathlib import Path

import discord
from crontab import CronTab

client = discord.Client()

async def send_message(interval, channel, text):
    await client.wait_until_ready()
    cron = CronTab(interval)
    while True:
        await asyncio.sleep(cron.next())
        try:
            await channel.send(text)
        except Exception:
            print(f"Could not send `{text}` to `{channel}:`")
            traceback.format_exc()

@client.event
async def on_ready():
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
        # Ignore blank lines
        if not line.strip():
            continue

        # Schedule tasks for valid lines
        try:
            interval, channel, text = line.split(',', 2)

            await client.wait_until_ready()
            channel = client.get_channel(int(channel.strip()))
            print(f"Found channel: {channel.name}, {channel.id}")
            text = text.strip()

            print(f'Scheduling `{text}` with schedule `{interval.strip()}`')
            client.loop.create_task(send_message(interval, channel, text))
        except Exception as err:
            print('Could not schedule task:')
            traceback.format_exc()
            raise

client.run(os.environ['FIRBOT_TOKEN'])
