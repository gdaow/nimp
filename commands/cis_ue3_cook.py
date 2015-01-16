# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
from commands.cis_command       import *
from utilities.ue3              import *
from utilities.ue3_deployment   import *

FARM_P4_PORT     = "192.168.1.2:1666"
FARM_P4_USER     = "CIS-CodeBuilder"
FARM_P4_PASSWORD = "CIS-CodeBuilder"

#-------------------------------------------------------------------------------
class CisUe3CookComman(CisCommand):
    abstract = 0
    def __init__(self):
        CisCommand.__init__(self, 'cis-ue3-cook', 'Cooks game and publishes result.')

    #---------------------------------------------------------------------------
    def configure_arguments(self, context, parser):
        CisCommand.configure_arguments(self, context, parser)
        settings = context.settings

        parser.add_argument('-r',
                            '--revision',
                            help    = 'Current revision',
                            metavar = '<revision>',
                            default = None)

        parser.add_argument('-p',
                            '--platform',
                            help    = 'platforms to publish',
                            metavar = '<platform>')

        parser.add_argument('-c',
                            '--configuration',
                            help    = 'Configurations to publish',
                            metavar = '<platform>',
                            choices = ['test', 'final'])

        parser.add_argument('--dlc',
                            help    = 'Dlc to cook',
                            metavar = '<platform>',
                            default = None)
        return True

    #---------------------------------------------------------------------------
    def _cis_run(self, context):
        settings  = context.settings
        arguments = context.arguments

        game             = settings.game
        project_name     = settings.project_name
        languages        = settings.languages
        platform         = arguments.platform
        dlc              = arguments.dlc
        map              = settings.cook_maps[(dlc or 'default').lower()]
        configuration    = arguments.configuration
        binary_revision  = get_latest_available_revision(settings.cis_version_directory,
                                                         platforms       = ['Win64', platform],
                                                         project         = project_name,
                                                         game            = game,
                                                         start_revision  =  arguments.revision)
        revision = arguments.revision

        if binary_revision is None:
            log_error("Unable to find binaries to cook revision {0}. Please build it.", revision)
            return False

        log_notification("Using binaries from revision {0}", arguments.revision)

        cook_destination = settings.cis_cook_directory if dlc is None else settings.cis_dlc_cook_directory

        if not deploy(settings.cis_version_directory,
                      project  = project_name,
                      game     = game,
                      revision = binary_revision,
                      platform = 'Win64'):
            log_error("Unable to deploy Win64 binaries")
            return False

        if dlc is not None:
            cook_revision = get_latest_available_revision(settings.cis_cook_directory,
                                                          platforms       = [platform],
                                                          project         = project_name,
                                                          game            = game,
                                                          configuration   = configuration,
                                                          start_revision  =  arguments.revision)
            if cook_revision is None:
                log_error("Unable to find Episode 01 cook. Please build it.", arguments.revision)
                return False

            log_notification("Using Episode 01 cook from revision {0}", revision)
            if not deploy(settings.cis_cook_directory,
                          project  = project_name,
                          game     = game,
                          revision = cook_revision,
                          platform = platform):
                log_error("Unable to deploy Episode 01 cook")
                return False

        if not ue3_cook(game, map, languages, dlc, platform, configuration):
            return False

        if not ue3_publish_cook(cook_destination, project_name, game, platform, configuration, revision, dlc):
            return False

        return True