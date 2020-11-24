cd /Volumes/SharedFolders/PlexMedia/PlexProcessing/TVMaze/Apps
echo $(date) "Starting Plex Watch Status Extract >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
/usr/local/bin/python3 plex_extract.py -p -w --vl=5
echo $(date) "Finished with Plex Cleanup >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
echo " "
