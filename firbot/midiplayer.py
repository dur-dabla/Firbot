# -*- coding: utf-8 -*-

import os
import io
import glob
import subprocess
from os import path

class MidiPlayer:
    """
    Play a midi file using timidity sequencer
    """

    # Midi files home
    MIDI_FILES_HOME = path.join(os.environ['HOME'], "midi")

    # Midi file extension
    MID_EXT = '.mid'

    # Sequencer command
    SEQUENCER_CMD  = 'timidity'
    # Sequencer aruments
    SEQUENCER_ARGS = [ '--quiet', '--quiet', '-Ow', '-o', '-' ]

    def get_full_path(self, song):
        for full_path in glob.iglob(path.join(self.MIDI_FILES_HOME, '*', '*' + self.MID_EXT), recursive=True):
            if path.basename(full_path).lower().startswith(song.lower()):
                return full_path

    def read(self, args) -> io.BufferedIOBase:
        """ Runs the sequencer subprocess and returns the standard output """
        song = args[0]
        path = self.get_full_path(song)

        args = args[1:]

        print(f"Song: {song} => {path}")
        print(f"Args: {list(args)}")

        if path is None:
            print(f"Song not found.")
            return None

        seq_process = subprocess.Popen([self.SEQUENCER_CMD] + self.SEQUENCER_ARGS + [path] + list(args), stdout=subprocess.PIPE)
        return seq_process.stdout

    def list_songs(self, args):
        available_categories = self.list_available_categories()

        if len(args) > 0:
            if args[0] in available_categories:
                categories = [args[0]]
            else:
                yield f"No such category : ``{args[0]}``."
                return
        else:
            categories = available_categories

        yield "Songs:"
        for cat in categories:
            yield f"> {cat}:"
            cat_dir = path.join(self.MIDI_FILES_HOME, cat)
            files = [f for f in os.listdir(cat_dir) if path.isfile(path.join(cat_dir, f)) and f.endswith(self.MID_EXT)]
            yield '```css\n' + '- ' + '\n- '.join(files) + '```'

    def list_playlists(self, args):
        available_categories = self.list_available_categories()
        yield 'Playlists:\n```css\n' + '- ' + '\n- '.join(available_categories) + '```'

    def list_available_categories(self):
        return [dir for dir in os.listdir(self.MIDI_FILES_HOME) if path.isdir(path.join(self.MIDI_FILES_HOME, dir))]

# Single instance
midiplayer = MidiPlayer()
