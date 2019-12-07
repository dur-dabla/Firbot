# -*- coding: utf-8 -*-

import os
import glob
from os import path

class Utils:
    # Midi files home
    MIDI_FILES_HOME = path.join(os.environ['HOME'], "midi")

    # Midi file extension
    MID_EXT = '.mid'

    def is_matching(self, str_ref, str_find):
        return str_ref.lower().startswith(str_find.lower())

    def get_full_path(self, song):
        for full_path in glob.iglob(path.join(self.MIDI_FILES_HOME, '*', '*' + self.MID_EXT), recursive=True):
            if self.is_matching(path.basename(full_path), song):
                return full_path

    def search_song(self, song):
        print(f"Searching {song}...")
        available_songs = self.list_available_songs()
        matching_songs = [s for s in available_songs if self.is_matching(s, song)]
        print(f"Matching songs : {matching_songs}")
        return matching_songs

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
            files = self.list_available_songs_in_category(cat_dir)
            yield '```css\n' + '- ' + '\n- '.join(files) + '```'

    def list_playlists(self, args):
        available_categories = self.list_available_categories()
        yield 'Playlists:\n```css\n' + '- ' + '\n- '.join(available_categories) + '```'

    def list_available_songs(self):
        available_songs = []
        for cat in self.list_available_categories():
            cat_dir = path.join(self.MIDI_FILES_HOME, cat)
            available_songs += self.list_available_songs_in_category(cat_dir)
        return available_songs

    def list_available_songs_in_category(self, cat_dir):
        return [f for f in os.listdir(cat_dir) if path.isfile(path.join(cat_dir, f)) and f.endswith(self.MID_EXT)]

    def list_available_categories(self):
        return [dir for dir in os.listdir(self.MIDI_FILES_HOME) if path.isdir(path.join(self.MIDI_FILES_HOME, dir))]

# Single instance
utils = Utils()
