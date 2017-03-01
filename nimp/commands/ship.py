# -*- coding: utf-8 -*-
# Copyright © 2014—2016 Dontnod Entertainment

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# 'Software'), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
''' Commands related to version packaging and shipping '''

import os
import shutil

import nimp.commands
import nimp.environment
import nimp.system
import nimp.p4

class Ship(nimp.command.Command):
    ''' Packages an unreal project for release '''
    def __init__(self):
        super(Ship, self).__init__()

    def configure_arguments(self, env, parser):
        nimp.command.add_common_arguments(parser, 'configuration', 'platform', 'revision')

        parser.add_argument('--destination',
                            help = 'Destination directory',
                            metavar = '<dir>')

        parser.add_argument('--package',
                            help = 'Override final package name',
                            default = 'default',
                            metavar = '<map>')

        parser.add_argument('--map',
                            help = 'Override default map',
                            default = '',
                            metavar = '<map>')

        return True

    def is_available(self, env):
        return nimp.unreal.is_unreal4_available(env)

    def run(self, env):
        if not env.check_config('publish_ship'):
            return False

        loose_dir = env.format(env.destination) if env.destination else env.format(env.publish_ship)
        exe_path = nimp.system.sanitize_path(os.path.join(env.format(env.root_dir), 'Engine/Binaries/DotNET/AutomationTool.exe'))
        # Use heartbeat because this sometimes compiles shaders in the background
        cmd = [ exe_path,
                'BuildCookRun',
                '-nocompileeditor', '-nop4',
                nimp.system.sanitize_path(env.format('-project={game}/{game}.uproject')),
                '-cook', '-stage', '-archive',
                '-archivedirectory=%s' % nimp.system.sanitize_path(loose_dir),
                '-package',
                env.format('-clientconfig={ue4_config}'),
                '-ue4exe=UE4Editor-Cmd.exe',
                '-crashreporter',
                '-pak',
                '-prereqs',
                '-nodebuginfo',
                env.format('-targetplatform={ue4_platform}'),
                '-utf8output' ]
        if env.map:
            cmd += [ env.format('-mapstocook={map}') ]

        #Ship._tweak_default_game_ini(env)
        success = nimp.system.call_process('.', cmd, heartbeat = 30) == 0
        #Ship._revert_default_game_ini(env)
        return success

    @staticmethod
    def _tweak_default_game_ini(env):
        original_default_game_ini = Ship._get_default_game_ini_path(env)
        tweaked_default_game_ini = os.path.splitext(original_default_game_ini)[0] + '.tweaked.ini'
        with open(tweaked_default_game_ini, 'w') as tweaked_ini:
            with open(original_default_game_ini, 'r') as original_ini:
                for line in original_ini:
                    if line.lower().startswith('projectversion='):
                        tweaked_ini.write('ProjectVersion=%s\n' % Ship._get_project_version_string(env))
                    else:
                        tweaked_ini.write(line)
        p4_client = nimp.p4.get_client(env)
        p4_client.edit('default', original_default_game_ini)
        shutil.move(tweaked_default_game_ini, original_default_game_ini)

    @staticmethod
    def _revert_default_game_ini(env):
        p4_client = nimp.p4.get_client(env)
        p4_client.revert('default', Ship._get_default_game_ini_path(env))

    @staticmethod
    def _get_default_game_ini_path(env):
        return nimp.system.sanitize_path(os.path.abspath(os.path.join(env.root_dir, env.game, 'Config', 'DefaultGame.ini')))

    @staticmethod
    def _get_project_version_string(env):
        last_deployed_revision = nimp.system.load_last_deployed_revision(env)
        return 'e%s-d%s' % (last_deployed_revision if last_deployed_revision is not None else '??????', env.revision)
