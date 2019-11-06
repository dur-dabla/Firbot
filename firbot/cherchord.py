# -*- coding: utf-8 -*-

import importlib.resources
import json
import subprocess

import colors

import firbot.data


class CherchordException(Exception):
    """
    Exception class to handle errors in custom cherchord extensions.
    """


class Cherchord:
    """
    Class to encapsulate the behaviour of the cherchord command line
    utility and to manage custom extensions.
    """

    # Map note string representation to integer
    __note_str_to_int = {
        note: integer
        for integer, note in enumerate(['Ab', 'A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G'])
    }

    # Map note integer representation to string
    __note_int_to_str = {
        integer: note
        for note, integer in __note_str_to_int.items()
    }

    def __init__(self):
        # Load instruments file
        with importlib.resources.open_text(firbot.data, 'cherchord-config.json') as fd:
            self.instruments: dict = json.load(fd)['instruments']

    def __call__(self, *args) -> str:
        """
        This function takes a command line input for the Haskell program
        cherchord and returns its result as a string.

        :param args: list of arguments to forward to cherchord
        :return: result of cherchord
        """
        # Handle --instruments to read the list of available instruments
        if len(args) == 1 and args[0] == '--instruments':
            yield "Instruments :\n" + '\n'.join([
                f'\N{EN DASH} {instrument} : `{notes}`'
                for instrument, notes in self.instruments.items()
            ])
            return

        # Handle custom extensions to the -i/--instrument option
        try:
            args = self.replace_instrument(args)
        except Exception as err:
            yield f"Error in -i: {err}"
            return

        try:
            # Run cherchord
            res = subprocess.run(['cherchord', *args], check=True, capture_output=True)
            # Decode & strip unneeded information
            res = colors.strip_color(res.stdout.decode('utf-8'))

            # Split tab lines in several messages to avoid the Discord character limit
            for res_line in res.split('\n\n'):
                res_line = res_line.rstrip()
                # Ignore empty lines
                if len(res_line) == 0:
                    continue
                # Add Discord code tags
                yield "```" + res_line + "```"

        except subprocess.CalledProcessError as err:
            yield err.stderr.decode('utf-8')

    def replace_instrument(self, args: tuple) -> list:
        """
        Replace the '-i' argument in the command line if it exists by the
        corresponding notes. The replacement list of instruments is loaded
        from the configuration file.

        The instrument name can be followed by /+n or /-n where n is a number
        of semitones to respectively tune up or down every string of the
        instrument.

        :param args: space-separated command line
        :return: modified command line
        """
        args = list(args)

        # Try to find an argument to specify the instrument
        for arg_name in ['-i', '--instrument']:
            try:
                index = args.index(arg_name)
                break
            except ValueError:
                continue
        else:
            # No such argument was found, return command line as is
            return args

        # An instrument argument was found, read its value
        try:
            instrument_value = args[index + 1]
        except IndexError:
            raise CherchordException("-i/--instrument passed without an instrument")

        # Parse the instrument name an modifier
        if '/' in instrument_value:
            name, modifier = instrument_value.split('/')
            try:
                modifier = int(modifier)
            except ValueError:
                raise CherchordException("invalid modifier")
        else:
            name = instrument_value
            modifier = None

        # The instrument is not in the config file, let cherchord handle it
        if name not in self.instruments:
            if modifier is None:
                raise CherchordException("modifiers can only be applied to instruments from --instruments")
            return args

        # Replace the name & modifier by a string understood by cherchord
        if modifier is None:
            args[index + 1] = self.instruments[name]
        else:
            strings = self.instruments[name].split(',')
            args[index + 1] = ','.join(self.tune_string(string, modifier) for string in strings)
        return args

    @classmethod
    def tune_string(cls, string: str, semitones: int) -> str:
        """
        Take an instrument representation (ex: D14) and returns the representation
        corresponding to said string tuned up or down by the given amount of
        semitones. A positive amount of semitones will tune up while a negative
        amount thereof will tune down.

        :param string: string representation (ex: D14)
        :param semitones: number of semitones to tune up
        :return: tuned string representation
        """
        # Compute the absolute note representation as an integral
        cutoff = 2 if string[1] == 'b' else 1
        note = cls.__note_str_to_int[string[:cutoff]]
        level = int(string[cutoff:])
        abs_note = 12 * level + note

        # Compute new string representation
        new_level, new_note = divmod(abs_note + semitones, 12)
        return cls.__note_int_to_str[new_note] + str(new_level)


# Single instance
cherchord = Cherchord()
