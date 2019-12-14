#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import asyncio
import datetime
import importlib.resources
import os
import traceback

import discord.ext.commands
import pytz
from crontab import CronTab

from firbot.cogs.midiplayer import MidiPlayer
import firbot.cherchord
import firbot.data

ADMIN_ROLE = "FirbotMaster"

bot = discord.ext.commands.Bot(command_prefix='!')
running_tasks = []

async def send_message(interval, channel, text):
    await bot.wait_until_ready()
    cron = CronTab(interval)
    while True:
        now = datetime.datetime.now(pytz.timezone("Europe/Paris"))
        await asyncio.sleep(cron.next(now=now))
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

@bot.event
async def on_message_edit(before, after):
    await bot.process_commands(after)

@bot.command()
async def cherchord(context, *args):
    for line in firbot.cherchord.cherchord(*args):
        await context.send(line)

@bot.command()
async def say(context, *args):
    """Simply make the bot say something in a channel"""
    print(f"Handle say {args}")

    if len(args) < 2:
        await context.send(f"{context.author.mention} Usage: `{bot.command_prefix}say [channel] [message]`.")

    for chan in bot.get_all_channels():
        print(f"Channel : {chan.name}")
        if chan.name == args[0]:
            await chan.send(" ".join(args[1:]))
            break

@bot.command()
async def quit(context):
    print(f"Handle quit")
    if ADMIN_ROLE in list(map(lambda r: r.name, context.author.roles)):
        await context.channel.send("Bye.")
        await bot.logout()
    else:
        print(f'Member {context.author.name} not allowed to run this command.')

# Commands: play, stop, songs, playlists
bot.add_cog(MidiPlayer(bot))

bot.run(os.environ['FIRBOT_TOKEN'])
