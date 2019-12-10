# -*- coding: utf-8 -*-

from . import utils

import io
import asyncio
import discord
import subprocess

from discord.ext import commands

class MidiPlayer(commands.Cog):
    """
    Play a midi file using timidity sequencer
    """

    # Sequencer command
    SEQUENCER_CMD  = 'timidity'
    # Sequencer aruments
    SEQUENCER_ARGS = [ '--quiet', '--quiet', '-Ow', '-o', '-' ]

    # Sequencer process
    seq_process = None

    def __init__(self, bot):
        self.bot = bot

    def after_play(self, error):
        print("Song finished.")
        coro = self.bot.change_presence(activity=None)
        fut = asyncio.run_coroutine_threadsafe(coro, self.bot.loop)
        try:
            fut.result()
        except:
            # an error happened changing the presence
            pass

    def read(self, song, args) -> io.BufferedIOBase:
        """ Runs the sequencer subprocess and returns the standard output """
        path = utils.get_full_path(song)
        print(f"Song: {song} => {path}")
        print(f"Args: {list(args)}")

        if path is None:
            print(f"Song not found.")
            return None

        self.seq_process = subprocess.Popen([self.SEQUENCER_CMD, *self.SEQUENCER_ARGS, path, *args], stdout=subprocess.PIPE)
        return self.seq_process.stdout

    def terminate(self):
        """Sends SIGTERM to the sequencer process"""
        if self.seq_process is not None:
            self.seq_process.terminate()
            self.seq_process = None

    @commands.command()
    async def play(self, context, *args):
        """Play a midi file"""
        print(f"Handle play [{args}]")

        if context.author.voice is None or context.author.voice.channel is None:
            await context.channel.send(f"{context.author.mention} You must be connected to a voice channel before to run this command.")
            return

        author_voice_channel = context.author.voice.channel
        voice_client = None

        for vc in self.bot.voice_clients:
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
        matching_songs = utils.search_song(args[0])
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
        stream = self.read(song, args)

        if stream is None:
            await context.channel.send(f"{context.author.mention} Unable to play this song.")
            await voice_client.disconnect()
            return

        src = discord.FFmpegPCMAudio(stream, pipe=True)
        await self.bot.change_presence(activity=discord.Game(song))
        voice_client.play(src, after=self.after_play)

    @commands.command()
    async def stop(self, context, *args):
        """Stop the playback then stop and disconnect all voice clients"""
        print(f"Handle stop")
        self.terminate()
        await self.bot.change_presence(activity=None)
        for i,vc in enumerate(self.bot.voice_clients):
            print(f"VoiceClient {i} :")
            if not vc.channel is None:
                print(f"`- Connected on {vc.channel.name}")
                print(f"`- Stopping music`")
                vc.stop()
                print(f"`- Disconnecting from channel`")
                await vc.disconnect()

    @commands.command()
    async def songs(self, context, *args):
        """List available midi files"""
        for line in utils.list_songs(args):
            await context.send(line)

    @commands.command()
    async def playlists(self, context, *args):
        """List available playlists"""
        for line in utils.list_playlists(args):
            await context.send(line)
