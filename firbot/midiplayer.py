# -*- coding: utf-8 -*-

import io
import subprocess

class MidiPlayer:
    """
    Play a midi file using timidity sequencer
    """

    # Sequencer command
    SEQUENCER_CMD  = 'timidity'
    # Sequencer aruments
    SEQUENCER_ARGS = [ '--quiet', '--quiet', '-Ow', '-o', '-' ]

    def read(self, *args) -> io.BufferedIOBase:
        """ Runs the sequencer subprocess and returns the standard output """
        seq_process = subprocess.Popen([self.SEQUENCER_CMD] + self.SEQUENCER_ARGS + list(args), stdout=subprocess.PIPE)
        return seq_process.stdout

# Single instance
midiplayer = MidiPlayer()
