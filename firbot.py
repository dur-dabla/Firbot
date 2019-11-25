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

import firbot.midiplayer
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


@bot.command()
async def cherchord(context, *args):
    for line in firbot.cherchord.cherchord(*args):
        await context.send(line)

@bot.command()
async def quit(context):
    print(f"Handle quit")
    if ADMIN_ROLE in list(map(lambda r: r.name, context.author.roles)):
        await context.channel.send("Bye.")
        await bot.logout()
    else:
        print(f'Member {context.author.name} not allowed to run this command.')

@bot.command()
async def play(context, *args):
    """Play a midi file"""
    print(f"Handle play [{args}]")

    if context.author.voice is None or context.author.voice.channel is None:
        await context.channel.send(f"{context.author.mention} You must be connected to a voice channel before to run this command.")
        return

    author_voice_channel = context.author.voice.channel
    voice_client = None

    for vc in bot.voice_clients:
        if vc.is_playing():
            await context.channel.send(f"{context.author.mention} Already playing in ``#{vc.channel.name}`` channel, please wait or run ``!stop`` command.")
            return
        if vc.channel == author_voice_channel:
            # Same channel
            voice_client = vc
        else:
            # Another channel
            await vc.disconnect()

    # Search the song
    matching_songs = firbot.midiplayer.midiplayer.search_song(args[0])
    matching_count = len(matching_songs)
    if matching_count != 1:
        if matching_count > 1:
            await context.channel.send(f"{context.author.mention} Available songs matching `{args[0]}`:\n" + '```css\n' + '- ' + '\n- '.join(matching_songs) + '```\nPlease be more accurate.')
        else:
            await context.channel.send(f"{context.author.mention} No song matching `{args[0]}` found.")
        return

    song = matching_songs[0]
    args = args[1:]

    # Connect to channel if not already connected
    if voice_client is None:
        voice_client = await author_voice_channel.connect()

    print(f"Playing on channel [{voice_client.channel.name}]")
    await context.channel.send(f"Playing `{song}` on channel `#{voice_client.channel.name}`.")
    stream = firbot.midiplayer.midiplayer.read(song, args)

    if stream is None:
        await context.channel.send(f"{context.author.mention} Unable to play this song.")
        await voice_client.disconnect()
        return

    src = discord.FFmpegPCMAudio(stream, pipe=True)
    voice_client.play(src)

@bot.command()
async def stop(context, *args):
    """Stop and disconnect all voice channels """
    print(f"Handle stop")
    for i,vc in enumerate(bot.voice_clients):
        print(f"VoiceClient {i} :")
        if not vc.channel is None:
            print(f"`- Connected on {vc.channel.name}")
            print(f"`- Stopping music`")
            vc.stop()
            print(f"`- Disconnecting from channel`")
            await vc.disconnect()

@bot.command()
async def songs(context, *args):
    """List available midi files"""
    for line in firbot.midiplayer.midiplayer.list_songs(args):
        await context.send(line)

@bot.command()
async def playlists(context, *args):
    """List available playlists"""
    for line in firbot.midiplayer.midiplayer.list_playlists(args):
        await context.send(line)

bot.run(os.environ['FIRBOT_TOKEN'])
