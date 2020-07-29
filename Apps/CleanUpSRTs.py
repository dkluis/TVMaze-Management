import os

allMediaFiles = open("/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/Apps/TempFiles/allfiles.txt")
files = allMediaFiles.read()
allMediaFiles.close()

records = files.split('\n')
records.sort()

recs = len(records)
ind = 0


def getFileName(path, suffix):
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


while ind < recs:
    if ind == 0:
        bef_check = "Current Record first record"
        ext_bef = "Empty"
        bef_name = "Empty"
    else:
        bef_check = records[ind - 1]
        ext_bef = bef_check.split(".")[- 1]
        bef_name = getFileName(records[ind - 1], ext_bef)

    cur_check = records[ind]
    ext_cur = cur_check.split(".")[- 1]
    cur_name = getFileName(records[ind], ext_cur)

    if ind == recs - 1:
        aft_check = "Current Records was last record"
        ext_aft = "Empty"
        aft_name = "Empty"
    else:
        aft_check = records[ind + 1]
        ext_aft = aft_check.split(".")[- 1]
        aft_name = getFileName(records[ind + 1], ext_aft)

    if ext_cur == "srt":
        if bef_name != cur_name and aft_name != cur_name:
            # print("Delete Candidate: ", records[ind])
            # print(bef_name)
            # print (cur_name)
            # print (aft_name)
            if os.path.isfile(records[ind]):
                print("Deleting: ", records[ind])
                os.remove(records[ind])
            else:
                print("File not Found: ", records[ind])

    ind = ind + 1
