#!/bin/bash

cd /Volumes/HD-Media-CA-Media/PlexMedia/PlexProcessing/TVMaze/Apps
echo $(date) "Starting Plex Watch Status Extract"
/usr/local/bin/python3 plex_extract.py --vl=5
echo $(date) "Finished with Plex Cleanup"
echo " "
