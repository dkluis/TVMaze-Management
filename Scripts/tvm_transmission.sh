#!/bin/zsh
### Setup Bash for Error Checking and Handling
## Setup catching variables that are not initialized
#
# set -o nounset
## Setup catching Exit errors and stopping the script
#
set -o errexit

### Setup the constants
##
#
Logfile="/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/Logs/Transmission.log"
# AppDir='/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/Apps'

# Position in the temp diretory
# cd $AppDir

echo $(date) "Transmission Started" >>$Logfile
echo $TR_TORRENT_NAME >>$Logfile
