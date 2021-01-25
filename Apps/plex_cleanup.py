
"""

plex_cleanup.py The App that handles all plex_cleanups by deleting the left over subtitles files
                and deleting the empty directories

Usage:
  plex_cleanup.py [--vl=<vlevel>]
  plex_cleanup.py -h | --help
  plex_cleanup.py --version

Options:
  -h --help      Show this screen
  --vl=<vlevel>  Level of verbosity (a = All, i = Informational, w = Warnings only) [default: w]
  --version      Show version.

"""

from docopt import docopt

from Libraries import logging, os


def get_the_args():
    o = docopt(__doc__, version='Shows Release 0.9.5')
    i = False
    w = True
    if o['--vl'].lower() == 'a':
        i = True
    elif o['--vl'].lower() == 'i':
        i = True
    if i:
        log.write(f'verbosity levels Informational {i} and Warnings {w}')
        log.write(o)
    return i, o


def get_file_names(path, suffix):
    name = False
    if path == "" or suffix == "":
        name = "Empty"
    else:
        if suffix == "srt":
            if '.en.srt' in path:
                name = str(path).split(".en.srt")[0]
            else:
                name = str(path).split('.srt')[0]
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
log = logging(caller='Cleanup', filename='Process')
log.open()
log.close()
log.start()

options = get_the_args()
vli = options[0]
vlw = options[1]

listoffiles = list()
listofdirs = list()
for (dirpath, dirnames, filenames) in os.walk('/Volumes/HD-Data-CA-Server/PlexMedia/TV Shows'):
    listoffiles += ([os.path.join(dirpath, file) for file in filenames])
    listofdirs += ([os.path.join(dirpath, dirn) for dirn in dirnames])
for (dirpath, dirnames, filenames) in os.walk('/Volumes/HD-Data-CA-Server/PlexMedia/Movies'):
    listofdirs += ([os.path.join(dirpath, dirn) for dirn in dirnames])
    listoffiles += ([os.path.join(dirpath, file) for file in filenames])
for (dirpath, dirnames, filenames) in os.walk('/Volumes/HD-Data-CA-Server/PlexMedia/Kids/TV Shows'):
    listofdirs += ([os.path.join(dirpath, dirn) for dirn in dirnames])
    listoffiles += ([os.path.join(dirpath, file) for file in filenames])
for (dirpath, dirnames, filenames) in os.walk('/Volumes/HD-Data-CA-Server/PlexMedia/Kids/Movies'):
    listofdirs += ([os.path.join(dirpath, dirn) for dirn in dirnames])
    listoffiles += ([os.path.join(dirpath, file) for file in filenames])

listofdirs.sort(reverse=True)
listoffiles.sort()
log.write(f'Number of files to process {len(listoffiles)}, in {len(listofdirs)} directories')

nfiles = len(listoffiles)
ind = 0
while ind < nfiles:
    if vli:
        log.write(f'Processing {ind}, {listoffiles[ind]}')
    if ind == 0:
        bef_check = "Current Record first record"
        ext_bef = "Empty"
        bef_name = "Empty"
    else:
        bef_check = listoffiles[ind - 1]
        ext_bef = bef_check.split(".")[- 1]
        bef_name = get_file_names(listoffiles[ind - 1], ext_bef)
    if vli:
        log.write(f'Before Information now is {bef_check}, {ext_bef}, {bef_name}')
    
    cur_check = listoffiles[ind]
    ext_cur = cur_check.split(".")[- 1]
    cur_name = get_file_names(listoffiles[ind], ext_cur)
    if vli:
        log.write(f'Current Information now is {cur_check}, {ext_cur}, {cur_name}')
    
    if ind == nfiles - 1:
        aft_check = "Current Record was last record"
        ext_aft = "Empty"
        aft_name = "Empty"
    else:
        aft_check = listoffiles[ind + 1]
        ext_aft = aft_check.split(".")[- 1]
        aft_name = get_file_names(listoffiles[ind + 1], ext_aft)
    if vli:
        log.write(f'After Information now is {aft_check}, {ext_aft}, {aft_name}')
    
    if ext_cur == "srt":
        if bef_name != cur_name and aft_name != cur_name:
            if vli:
                log.write("Delete Candidate: ", listoffiles[ind])
                log.write(bef_name)
                log.write(cur_name)
                log.write(aft_name)
            if os.path.isfile(listoffiles[ind]):
                try:
                    os.remove(listoffiles[ind])
                    log.write("Deleted: ", listoffiles[ind])
                except OSError as err:
                    log.write(f'Delete Failed for {listoffiles[ind]} with error {err}')
            else:
                log.write("File not Found: ", listoffiles[ind])
    
    ind = ind + 1

for d in listofdirs:
    try:
        os.remove(f'{d}/.DS_Store')
        if vli:
            log.write(f'Deleted a .DS_Store for {d}')
    except OSError as err:
        pass
    
    if vli:
        log.write(d)
    try:
        if vli:
            log.write(f'Directory is {len(os.listdir(d))}, {os.listdir(d)}')
        os.removedirs(d)
        log.write(f'Removed {d}')
    except OSError as err:
        if vli:
            log.write(f'Error Occurred Deleting Directory {err}')
        if str(err)[:10] != '[Errno 66]' and str(err)[:9] != '[Errno 2]':
            log.write(err)

log.end()
quit()
