

cd /Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/Apps
echo $(date) "Starting Plex Cleanup"

python3 plex_cleanup.py --vl=i

echo $(date) "Finished with Plex Cleanup"
echo " "
echo " "