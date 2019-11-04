# -*- coding: utf-8 -*-

import subprocess


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
        # Strip unneeded information
        res = res.stdout.decode('utf-8')
        res = '\n'.join(res.splitlines()[3:])
        # Add Discord code tags
        return "```" + res + "```"
    except subprocess.CalledProcessError as err:
        return err.stderr.decode('utf-8')
