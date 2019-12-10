# -*- coding: utf-8 -*-

import os
import glob
from os import path

# Midi files home
MIDI_FILES_HOME = path.join(os.environ['HOME'], "midi")

# Midi file extension
MID_EXT = '.mid'

def is_matching(str_ref, str_find):
    return str_ref.lower().startswith(str_find.lower())

def get_full_path(song):
    for full_path in glob.iglob(path.join(MIDI_FILES_HOME, '*', '*' + MID_EXT), recursive=True):
        if is_matching(path.basename(full_path), song):
            return full_path

def search_song(song):
    print(f"Searching {song}...")
    available_songs = list_available_songs()
    matching_songs = [s for s in available_songs if is_matching(s, song)]
    print(f"Matching songs : {matching_songs}")
    return matching_songs

def list_songs(args):
    available_categories = list_available_categories()

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
        cat_dir = path.join(MIDI_FILES_HOME, cat)
        files = list_available_songs_in_category(cat_dir)
        yield '```css\n' + '- ' + '\n- '.join(files) + '```'

def list_playlists(args):
    available_categories = list_available_categories()
    yield 'Playlists:\n```css\n' + '- ' + '\n- '.join(available_categories) + '```'

def list_available_songs():
    available_songs = []
    for cat in list_available_categories():
        cat_dir = path.join(MIDI_FILES_HOME, cat)
        available_songs += list_available_songs_in_category(cat_dir)
    return available_songs

def list_available_songs_in_category(cat_dir):
    return [f for f in os.listdir(cat_dir) if path.isfile(path.join(cat_dir, f)) and f.endswith(MID_EXT)]

def list_available_categories():
    return [dir for dir in os.listdir(MIDI_FILES_HOME) if path.isdir(path.join(MIDI_FILES_HOME, dir))]
