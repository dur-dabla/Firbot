#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup


setup(
   name='firbot',
   version='1.0',
   description='Simple bot for the Dur Dabla Discord server',
   license='MIT',
   author='Dur Dabla',
   packages=['firbot'],
   install_requires=[
       'crontab',
       'discord'
   ]
)
