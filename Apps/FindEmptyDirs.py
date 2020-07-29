import os
import shutil

# Create a List of Directories to check
dirNames = ['/Volumes/HD-Data-CA-Server/PlexMedia/TV Shows', '/Volumes/HD-Data-CA-Server/PlexMedia/Movies',
            '/Volumes/HD-Data-CA-Server/PlexMedia/Series', '/Volumes/HD-Data-CA-Server/PlexMedia/Kids']

listOfEmptyDirs = list()

# Iterate over the list of directories and their directory trees and check if any directory is empty.
for checkdirs in dirNames:
    for (dirpath, dirnames, filenames) in os.walk(checkdirs):
        filenames = [f for f in filenames if not f[0] == '.']
        # print(filenames)
        if len(dirnames) == 0 and len(filenames) == 0:
            listOfEmptyDirs.append(dirpath)

for toDeleteDir in listOfEmptyDirs:
    shutil.rmtree(toDeleteDir)
    print("Deleted Directory: ", toDeleteDir)
