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
        res = subprocess.run(['cherchord', *args], check=True, capture_output=True)
        return res.stdout
    except subprocess.CalledProcessError as err:
        return err.stderr
