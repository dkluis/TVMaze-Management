#!/bin/zsh

### Automatic Script after Transmission download complete
###   to move the video to the right Plex Directory
###
##
#



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

echo $(date) "Swift Transmission started" >>$Logfile
echo "$TR_TORRENT_NAME" >>$logfile

