# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------
from commands.command       import *

from utilities.files        import *
from utilities.hashing      import *
from utilities.paths        import *
from utilities.processes    import *

if OS == WINDOWS:
    import _winreg
    from utilities.windows_utilities            import *

#-------------------------------------------------------------------------------
# Ue3LooseFilesCommand
#-------------------------------------------------------------------------------
class Ue3LooseFilesCommand(Command):

    def __init__(self):
        Command.__init__(self, "ue3-loose", "Generate loose files")

    #---------------------------------------------------------------------------
    # configure_arguments
    def configure_arguments(self, context, parser):
        settings = context.settings

        parser.add_argument('-p',
                            '--platforms',
                            help      = 'Platforms to build',
                            metavar   = "PLATFORM",
                            nargs     = '*',
                            default   = settings.default_ue3_platforms,
                            choices   = settings.ue3_platforms)

        parser.add_argument('-r',
                             '--rebuild',
                             help     = 'Rebuild specified targets/platforms',
                             default  = False,
                             action   = "store_true")
        return True

    #---------------------------------------------------------------------------
    # run
    def run(self, context):
        settings = context.settings
        executable = os.path.join(settings.ue3_directory, "Binaries", "Win64", settings.ue3_game + ".exe")

        call_process(".", executable)
