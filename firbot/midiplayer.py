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
            if path.basename(full_path) == song:
                return full_path

    def read(self, *args) -> io.BufferedIOBase:
        """ Runs the sequencer subprocess and returns the standard output """
        song = args[0]
        path = self.get_full_path(song)

        print(f"Song: {song} => {path}")
        print(f"Args: {list(args[1:])}")
        seq_process = subprocess.Popen([self.SEQUENCER_CMD] + self.SEQUENCER_ARGS + [path] + list(args[1:]), stdout=subprocess.PIPE)
        return seq_process.stdout

    def list(self):
        yield "Playlist:"
        categories = [dir for dir in os.listdir(self.MIDI_FILES_HOME) if path.isdir(path.join(self.MIDI_FILES_HOME, dir))]
        for cat in categories:
            yield f"> {cat}:"
            cat_dir = path.join(self.MIDI_FILES_HOME, cat)
            files = [f for f in os.listdir(cat_dir) if path.isfile(path.join(cat_dir, f)) and f.endswith(self.MID_EXT)]
            yield '```markdown\n' + '- ' + '\n- '.join(files) + '```'


# Single instance
midiplayer = MidiPlayer()
