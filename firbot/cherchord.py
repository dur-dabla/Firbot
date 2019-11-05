# -*- coding: utf-8 -*-

import subprocess

import colors


def run_cherchord(*args) -> str:
    """
    This function takes a command line input for the Haskell program
    cherchord and returns its result as a string.

    :param args: list of arguments to forward to cherchord
    :return: result of cherchord
    """
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
