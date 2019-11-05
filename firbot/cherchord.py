# -*- coding: utf-8 -*-

import importlib.resources
import json
import subprocess

import colors

import firbot.data


class Cherchord:
    """
    Class to encapsulate the behaviour of the cherchord command line
    utility and to manage custom extensions.
    """
    def __init__(self):
        # Load instruments file
        with importlib.resources.open_text(firbot.data, 'cherchord-config.json') as fd:
            self.instruments = json.load(fd)['instruments']

    def __call__(self, *args) -> str:
        """
        This function takes a command line input for the Haskell program
        cherchord and returns its result as a string.

        :param args: list of arguments to forward to cherchord
        :return: result of cherchord
        """
        args = self.replace_instrument(args)

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

        :param args: space-separated command line
        :return: modified command line
        """
        args = list(args)

        for arg_name in ['-i', '--instrument']:
            try:
                index = args.index(arg_name)
                name = args[index + 1]
                if name in self.instruments:
                    args[index + 1] = self.instruments[name]
                return args
            except IndexError:
                continue
        return args


# Single instance
cherchord = Cherchord()
