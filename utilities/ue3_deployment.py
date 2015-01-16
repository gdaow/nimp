# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
import socket
import random
import string
import time
import contextlib
import shutil

from utilities.build        import *
from utilities.deployment   import *

#---------------------------------------------------------------------------
def ue3_publish_binaries(destination_format, project, game, revision, platform, configuration = None):
    publisher = FilePublisher(destination_format, project = None, game = None, platform = None, configuration = None, dlc = None, language = None, revision = revision)
    publisher.delete_destination()

    if (platform == 'Win32' or platform == 'Win64'):
        if configuration == 'Release' or configuration is None:
            publisher.add("Binaries\\{platform}\\{game}.exe")
            publisher.add("Binaries\\{platform}\\{game}.exe.config")
            publisher.add("Binaries\\{platform}\\{game}.config")
            publisher.add("Binaries\\{platform}\\{game}.com")
            publisher.add("Binaries\\Xbox360\\Interop.XDevkit.1.0.dll")
            publisher.add("Binaries\\PS3\\PS3Tools_x64.dll")
            publisher.add("Binaries\\Xbox360\\Xbox360Tools_x64.dll")
            publisher.add("Binaries\\Orbis\\OrbisTools_x64.dll")
            publisher.add("Binaries\\Dingo\\DingoTools_x64.dll")

            publisher.add("Binaries\\Win64\\Microsoft.VC90.CRT",    ['*.*'])
            publisher.add("Binaries\\{platform}",                   ['*.dll'], recursive = False )
            publisher.add("Binaries\\",                             ['*.xml', '*.bat', '*.dll', '*.exe.config', '*.exe'], recursive = False)
            publisher.add("Binaries\\Win64\\Editor\\Release",       ['*.*'], recursive = False)
            publisher.add("Binaries\\{platform}", ['{game}.*'], ['*.pdb', '*.map', '*.lib'], recursive = False)

        if configuration != 'Release':
            publisher.add("Binaries\\{platform}\\", ['{game}-{platform}-{configuration}.*'], ['*.pdb', '*.map', '*.lib'])

    if (platform != 'Win32' and platform != 'Win64'):
        if configuration is None:
            publisher.add("Binaries\\{platform}\\", ['{game}*-*.*'], ['*.pdb', '*.map', '*.lib'])
        else:
            publisher.add("Binaries\\{platform}\\", ['{game}-{platform}-{configuration}.*'], ['*.pdb', '*.map', '*.lib'])

    return True

#---------------------------------------------------------------------------
def ue3_publish_version(destination_format, project, game, revision, platform):
    if not ue3_publish_binaries(destination_format, project, game, revision, platform, None):
        return False

    publisher = FilePublisher(destination_format, project, game, platform, configuration = None, dlc = None, language = None, revision = revision)

    if platform.lower() == 'win64':
        publisher.add("{game}\\Script\\", ['*.*'])
        publisher.add("{game}\\ScriptFinalRelease\\", ['*.*'])

    return True

#---------------------------------------------------------------------------
def ue3_publish_cook(destination_format, project, game, platform, configuration, revision, dlc):
    publisher = FilePublisher(destination_format, project, game, platform, configuration = configuration, revision = revision, dlc = dlc, language = None)

    cook_platform = platform

    if platform.lower() == 'win64':
        platform = 'PC'
    if platform.lower() == 'win32':
        platform = 'PCConsole'

    suffix = 'Final' if configuration in ['test', 'final'] else ''

    if dlc is None:
        cook_directory = '{game}\\' + 'Cooked{0}{1}'.format(cook_platform, suffix)
    else:
        cook_directory = '{game}\\DLC\\{platform}\\{dlc}\\' + 'Cooked{0}{1}'.format(cook_platform, suffix)

    publisher.add(cook_directory)

    return True