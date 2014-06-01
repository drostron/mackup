"""
Keep your application settings in sync.

Copyright (C) 2013 Laurent Raufaste <http://glop.org/>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import os

from .appsdb import ApplicationsDatabase
from .application import ApplicationProfile
from .constants import (BACKUP_MODE,
                        RESTORE_MODE,
                        UNINSTALL_MODE,
                        LIST_MODE,
                        VERSION)
from .mackup import Mackup
from . import utils

class ColorFormatCodes:
    BLUE   = '\033[34m'
    BOLD   = '\033[1m'
    NORMAL = '\033[0m'

def header(str):
    return ColorFormatCodes.BLUE + str + ColorFormatCodes.NORMAL

def bold(str):
    return ColorFormatCodes.BOLD + str + ColorFormatCodes.NORMAL

def main():
    """Main function"""

    # Get the command line arg
    args = utils.parse_cmdline_args()

    mckp = Mackup()
    app_db = ApplicationsDatabase()

    def foreachApp(apps, f):
        for app_name in apps:
            if args.verbose: print(("{0} {1} {0}").format(header("---"), bold(app_name)))
            f(app_name)
            if args.verbose: print

    if args.mode == BACKUP_MODE:
        # Check the env where the command is being run
        mckp.check_for_usable_backup_env()

        def backupApplication(app_name):
            ApplicationProfile(mckp, app_db.get_files(app_name), args.dry_run, args.verbose).backup()
            
        foreachApp(mckp.get_apps_to_backup(), backupApplication)

    elif args.mode == RESTORE_MODE:
        # Check the env where the command is being run
        mckp.check_for_usable_restore_env()

        def restoreApplication(app_name):
          ApplicationProfile(mckp, app_db.get_files(app_name), args.dry_run, args.verbose).restore()

        foreachApp(mckp.get_apps_to_backup(), restoreApplication)

    elif args.mode == UNINSTALL_MODE:
        # Check the env where the command is being run
        mckp.check_for_usable_restore_env()

        if args.dry_run or \
           utils.confirm("You are going to uninstall Mackup.\n"
                         "Every configuration file, setting and dotfile"
                         " managed by Mackup will be unlinked and moved back"
                         " to their original place, in your home folder.\n"
                         "Are you sure ?"):

            def uninstallApp(app_name):
                ApplicationProfile(mckp, app_db.get_files(app_name), args.dry_run, args.verbose).uninstall()
            
            foreachApp(mckp.get_apps_to_backup(), uninstallApp)

            # Delete the Mackup folder in Dropbox
            # Don't delete this as there might be other Macs that aren't
            # uninstalled yet
            # delete(mckp.mackup_folder)

            print ("\n"
                   "All your files have been put back into place. You can now"
                   " safely uninstall Mackup.\n"
                   "\n"
                   "Thanks for using Mackup !"
                   .format(os.path.abspath(__file__)))

    elif args.mode == LIST_MODE:
        # Display the list of supported applications
        mckp.check_for_usable_environment()
        output = "Supported applications:\n"
        for app_name in sorted(app_db.get_app_names()):
            output += " - {}\n".format(app_name)
        output += "\n"
        output += ("{} applications supported in Mackup v{}"
                   .format(len(app_db.get_app_names()), VERSION))
        print output
    else:
        raise ValueError("Unsupported mode: {}".format(args.mode))

    # Delete the tmp folder
    mckp.clean_temp_folder()
