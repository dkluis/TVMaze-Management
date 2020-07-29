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
# printenv

echo "$(date) TVMaze Half Hourly Update Started"
echo ""
echo ""
echo "$(date) Downloads Move to Plex and Episode Status Update to TVMaze"
python3 swift_rep.py
echo ""
echo ""
echo "$(date) TVMaze Shows"
python3 shows.py -u 
echo ""
echo ""
echo "$(date) TVMaze Episodes"
python3 episodes.py 
echo ""
echo ""
echo "$(date) TVMaze Downloads"
python3 actions.py -d 
echo ""
echo ""
echo "$(date) TVMaze Statistics Update"
python3 statistics.py -s
echo ""
echo ""
echo "$(Date) TVMaze TVMaze Half Hourly Update Finished"
echo ""
echo ""
