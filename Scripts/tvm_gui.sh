### Setup zshell for Error Checking and Handling
## Setup catching variables that are not initialized
#
set -o nounset
## Setup catching Exit errors and stopping the script
#
set -o errexit

TVMDir='/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/Apps'
TVMLogs='/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/Logs'


### Spawning the next shell script, so that it can be tested and run by cron
##
#

# Position in the temp directory
cd $TVMDir

PYTHONPATH=/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages
export PYTHONPATH

# echo "$(date) TVMaze Episode Downloads"
python3 try_gui.py -u >$TVMLogs/gui.log 2>$TVMLogs/gui_err.log
