### Setup zshell for Error Checking and Handling
## Setup catching variables that are not initialized
#
set -o nounset
## Setup catching Exit errors and stopping the script
#
set -o errexit

AppDir='/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/Apps'
LogDir='/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/Logs'

### Spawning the next shell script, so that it can be tested and run by cron
##
#

# Position in the temp directory
cd $AppDir
PYTHONPATH=/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages
export PYTHONPATH
PATH=/Library/Frameworks/Python.framework/Versions/3.8/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/Library/Apple/usr/bin

export PATH
echo ''
echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"

python3 plex_tvm_update.py --vl=2
python3 shows.py -u --vl=2
python3 episodes.py --vl=2
python3 actions.py -d --vl=2
python3 statistics.py -s --vl=2

echo "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
echo ''