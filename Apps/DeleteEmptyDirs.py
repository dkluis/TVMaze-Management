import os
import shutil

# Create a List of Directories to check
dirsToCheck = ['/Volumes/HD-Data-CA-Server/PlexMedia/TV Shows', '/Volumes/HD-Data-CA-Server/PlexMedia/Movies',
               '/Volumes/HD-Data-CA-Server/PlexMedia/Series', '/Volumes/HD-Data-CA-Server/PlexMedia/Kids']

listOfEmptyDirs = list()


# Iterate over the list of directories and their directory trees and check if any directory is empty.
def findemptydirs():
    for checkDirs in dirsToCheck:
        for (dirPath, dirNames, filenames) in os.walk(checkDirs):
            filenames = [f for f in filenames if not f[0] == '.']
            if len(dirNames) == 0 and len(filenames) == 0:
                listOfEmptyDirs.append(dirPath)


# Delete all Empty Directories found
def deleteemptydirs():
    for toDeleteDir in listOfEmptyDirs:
        shutil.rmtree(toDeleteDir)
        print("Deleted Directory: ", toDeleteDir)


# Execute the lowest level of Empty Directories
print("Starting to delete the empty Season Level Directories")
findemptydirs()
deleteemptydirs()

# Execute the next level of Empty Directories
# We only expect 2 levels
# Example:   Delete the season level directories then the TV Show level
print("Starting to delete the empty TV Show level Directories")
findemptydirs()
deleteemptydirs()
