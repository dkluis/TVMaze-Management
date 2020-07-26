### Setup zshell for Error Checking and Handling
## Setup catching variables that are not initialized
#
set -o nounset
## Setup catching Exit errors and stopping the script
#
set -o errexit

TVMDir='/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze'

### Spawning the next shell script, so that it can be tested and run by cron
##
#

# Position in the temp directory
cd $TVMDir

PYTHONPATH=/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages
export PYTHONPATH
PATH=/Library/Frameworks/Python.framework/Versions/3.8/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/Library/Apple/usr/bin
export PATH
# printenv

echo "$(date) TVMaze Download Episodes Started"

echo "$(date) Episode Download Updates Started"
python3 transmission.py

echo "$(date) TVMaze Shows"
python3 shows.py -u 

echo "$(date) TVMaze Episodes"
python3 episodes.py 

echo "$(date) TVMaze Downloads"
python3 actions.py -d 

echo "$(date) TVMaze Statistics Update"
python3 statistics.py -s

echo "$(Date) TVMaze Download Episodes Finished"
echo ""
echo ""
