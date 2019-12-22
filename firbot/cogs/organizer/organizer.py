# -*- coding: utf-8 -*-

import caldav
import asyncio
import discord
from discord.ext import commands
import importlib
import json
from collections import namedtuple
from caldav.elements import dav
from icalendar import Calendar,Event

import firbot.data

CALDAV_NAMESPACE  = "{urn:ietf:params:xml:ns:caldav}"
CARDDAV_NAMESPACE = "{urn:ietf:params:xml:ns:carddav}"

ServerConfig = namedtuple('ServerConfig', ['url', 'username', 'password'])

class Organizer(commands.Cog):
    """
    Organizer
    """

    def __init__(self, bot):
        # Load config file
        with importlib.resources.open_text(firbot.data, 'caldav-config.json') as config_file:
            server_config = ServerConfig(**json.load(config_file)['server'])

        print(f"{server_config}")
        self.client = caldav.davclient.DAVClient(server_config.url, username=server_config.username, password=server_config.password)

    def is_matching(self, str_ref, str_find):
        return str_ref.lower().startswith(str_find.lower())

    def search_calendar(self, name):
        principal = self.client.principal()

        for cal in principal.calendars():
            if cal.name is not None:
                if self.is_matching(cal.name, name):
                    return cal
        return None

    @commands.command()
    async def todos(self, context, *args):
        """List tasks in a calendar"""
        print(f"Handle todos [{args}]")

        if len(args) < 1:
            await context.send(f"{context.author.mention} Please specify calendar name.")

        cal_name = args[0]

        try:
            calendar = self.search_calendar(cal_name)
        except:
            await context.send(f"{context.author.mention} An error occured.")
        if calendar is None:
            await context.send(f"{context.author.mention} Calendar `{cal_name}` not found.")

        print(calendar)
        todos = calendar.todos()
        if len(todos) == 0:
            await context.send(f"No todos in `{calendar.name}`.")
            return

        for i,todo in enumerate(todos):
            print(f"Todo {i} : {todo}")
            print()
            ics = todo.load()
            print(f"ICS:\n{ics.data}")
            print()
            c = Calendar.from_ical(ics.data)
            for td in c.walk('vtodo'):
                print(f"Todo: {td}")
                await context.send(f">>> __{td.get('summary')}__ : {td.get('status')}\nProgress: *{td.get('percent-complete')}%*\n```markdown\n{td.get('description')}\n```")

    @commands.command()
    async def events(self, context, *args):
        """List events in a calendar"""
        print(f"Handle events [{args}]")

        if len(args) < 1:
            await context.send(f"{context.author.mention} Please specify calendar name.")

        cal_name = args[0]

        try:
            calendar = self.search_calendar(cal_name)
        except:
            await context.send(f"{context.author.mention} An error occured.")
        if calendar is None:
            await context.send(f"{context.author.mention} Calendar `{cal_name}` not found.")

        events = calendar.events()
        if len(events) == 0:
            await context.send(f"No events in `{calendar.name}`.")
            return

        for i,event in enumerate(events):
            print(f"Event {i} : {event}")
            print()
            ics = event.load()
            print(f"ICS:\n{ics.data}")
            print()
            c = Calendar.from_ical(ics.data)
            for e in c.walk('vevent'):
                print(f"Event: {e}")
                await context.send(f">>> __{e.get('summary')}__ : {e.get('dtstart').dt}\nPlace: *{e.get('location')}*\n```markdown\n{e.get('description')}\n```")

    @commands.command()
    async def collections(self, context, *args):
        """List collections"""
        print(f"Handle collections [{args}]")

        if self.client is None:
            await context.send("An error occured.")
            return

        principal = self.client.principal()
        if principal is None:
            await context.send("An error occured.")
            return

        for cal in principal.calendars():
            print(cal.get_properties([dav.ResourceType(),dav.DisplayName()]))

        await context.send(f"__Principal:__\n{principal}")
        await context.send("__Calendars:__")
        for c in principal.children(type=f"{CALDAV_NAMESPACE}calendar"):
            await context.send(f"*{c[2]}:*\n{c[0]}")
        await context.send("__Adress Books:__")
        for c in principal.children(type=f"{CARDDAV_NAMESPACE}addressbook"):
            await context.send(f"*{c[2]}:*\n{c[0]}")
