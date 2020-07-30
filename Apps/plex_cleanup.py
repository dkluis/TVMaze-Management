import os


def getFileName(path, suffix):
    name = False
    if path == "" or suffix == "":
        name = "Empty"
    else:
        if suffix == "srt":
            name = str(path).split(".en.srt")[0]
        elif suffix == "mkv":
            name = str(path).split(".mkv")[0]
        elif suffix == "mp4":
            name = str(path).split(".mp4")[0]
        elif suffix == "avi":
            name = str(path).split(".avi")[0]
    return name


''' Main Program
    First collect all files and then all directories
    Process the SRT (subtitles) left without the video file and delete those
    Process all directories and delete empties
'''

listoffiles = list()
for (dirpath, dirnames, filenames) in os.walk('/Volumes/HD-Data-CA-Server/PlexMedia/TV Shows'):
    listoffiles += ([os.path.join(dirpath, file) for file in filenames])
for (dirpath, dirnames, filenames) in os.walk('/Volumes/HD-Data-CA-Server/PlexMedia/Movies'):
    listoffiles += ([os.path.join(dirpath, file) for file in filenames])
for (dirpath, dirnames, filenames) in os.walk('/Volumes/HD-Data-CA-Server/PlexMedia/Kids'):
    listoffiles += ([os.path.join(dirpath, file) for file in filenames])
listoffiles.sort()

listofdirs = list()
for (dirpath, dirnames, filenames) in os.walk('/Volumes/HD-Data-CA-Server/PlexMedia/TV Shows'):
    listofdirs += ([os.path.join(dirpath, dirn) for dirn in dirnames])
for (dirpath, dirnames, filenames) in os.walk('/Volumes/HD-Data-CA-Server/PlexMedia/Movies'):
    listofdirs += ([os.path.join(dirpath, dirn) for dirn in dirnames])
for (dirpath, dirnames, filenames) in os.walk('/Volumes/HD-Data-CA-Server/PlexMedia/Kids/TV Shows'):
    listofdirs += ([os.path.join(dirpath, dirn) for dirn in dirnames])
for (dirpath, dirnames, filenames) in os.walk('/Volumes/HD-Data-CA-Server/PlexMedia/Kids/Movies'):
    listofdirs += ([os.path.join(dirpath, dirn) for dirn in dirnames])

listofdirs.sort(reverse=True)
print(f'Number of files to process {len(listoffiles)}, in {len(listofdirs)} directories')

nfiles = len(listoffiles)
ind = 0
while ind < nfiles:
    # print(f'Processing {ind}, {listoffiles[ind]}')
    if ind == 0:
        bef_check = "Current Record first record"
        ext_bef = "Empty"
        bef_name = "Empty"
    else:
        bef_check = listoffiles[ind - 1]
        ext_bef = bef_check.split(".")[- 1]
        bef_name = getFileName(listoffiles[ind - 1], ext_bef)
    # print(f'Before Information now is {bef_check}, {ext_bef}, {bef_name}')
    
    cur_check = listoffiles[ind]
    ext_cur = cur_check.split(".")[- 1]
    cur_name = getFileName(listoffiles[ind], ext_cur)
    # print(f'Current Information now is {cur_check}, {ext_cur}, {cur_name}')
    
    if ind == nfiles - 1:
        aft_check = "Current Record was last record"
        ext_aft = "Empty"
        aft_name = "Empty"
    else:
        aft_check = listoffiles[ind + 1]
        ext_aft = aft_check.split(".")[- 1]
        aft_name = getFileName(listoffiles[ind + 1], ext_aft)
    # print(f'After Information now is {aft_check}, {ext_aft}, {aft_name}')
    
    if ext_cur == "srt":
        if bef_name != cur_name and aft_name != cur_name:
            # print("Delete Candidate: ", listoffiles[ind])
            # print(bef_name)
            # print(cur_name)
            # print(aft_name)
            if os.path.isfile(listoffiles[ind]):
                print("Deleting: ", listoffiles[ind])
                os.remove(listoffiles[ind])
            else:
                print("File not Found: ", listoffiles[ind])
    
    ind = ind + 1

for d in listofdirs:
    # print(d)
    try:
        os.removedirs(d)
        print(f'Removed {d}')
        quit()
    except OSError as err:
        # print(str(err)[:10])
        if str(err)[:10] != '[Errno 66]':
            print(err)
