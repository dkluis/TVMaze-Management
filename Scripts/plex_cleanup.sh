# Script to collect .srt, .mkv, and .mp4 files from PlexMedia
# only for the tv and movie directories
# Purpose:  Feed a python script with the list to compare

cd /Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/Apps/TempFiles
echo $(date) "Starting Plex Cleanup" 

rm allfiles.txt
rm tvfiles.txt
rm movfiles.txt
rm kidsfiles.txt

find /Volumes/HD-Data-CA-Server/PlexMedia/'TV Shows' -name "*.*" | grep -e '.srt' -e '.mp4' -e '.mkv' -e '.avi' > tvfiles.txt
find /Volumes/HD-Data-CA-Server/PlexMedia/Movies -name "*.*" | grep -e '.srt'  -e '.mp4' -e '.mkv' -e '.avi' > movfiles.txt
find /Volumes/HD-Data-CA-Server/PlexMedia/Kids -name "*.*" | grep -e '.mp4' -e ".srt" -e ".mkv" -e '.avi' > kidsfiles.txt
find /Volumes/HD-Data-CA-Server/PlexMedia/Series -name "*.*" | grep -e '.mp4' -e ".srt" -e ".mkv" -e '.avi' > seriesfiles.txt

sort kidsfiles.txt movfiles.txt seriesfiles.txt tvfiles.txt -o allfiles.txt 

cd ..

# echo "Starting Python Script to clean up the SRTs" 
python3 ./CleanUpSRTs.py 

# echo "Starting Python Script to delete Empty Directories"
python3 ./FindEmptyDirs.py 

# echo "Starting Python Script to delete Top Level Empty Directories" 
python3 ./FindEmptyDirs.py 

echo $(date) "Finished with Plex Cleanup" 
echo " "
echo " "