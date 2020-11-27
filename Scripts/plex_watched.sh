cd /Volumes/SharedFolders/PlexMedia/PlexProcessing/TVMaze/Apps
echo " "
echo $(date) "Starting Plex Watch Status Extract >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"

/usr/local/bin/python3 plex_extract.py -p -w --vl=2

echo $(date) "Finished with Plex Cleanup >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
echo " "
