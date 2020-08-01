import subprocess
import requests
from terminal_lib import *
from tvm_lib import *


def clear_subscreen(lines):
    idx = 0
    print(term_pos(menu_pos.sub_screen_x, menu_pos.menu_y) + term_codes.cl_eol)
    while idx <= lines:
        print(term_codes.cl_eol)
        idx = idx + 1


def clear_shows(lines):
    idx = 0
    print(term_pos(menu_pos.sub_screen_x, menu_pos.menu_2y) + term_codes.cl_eol)
    while idx < lines:
        print(term_pos(menu_pos.sub_screen_x + idx, menu_pos.menu_2y) + term_codes.cl_eol)
        idx = idx + 1


def display_menu(clear):
    if clear:
        print(term_codes.cl_scr)
    
    print(term_pos(menu_pos.top, menu_pos.menu_2y - 10) + term_codes.bold + term_codes.green +
          release.console_description + term_codes.red + " -> " + release.console_version + term_codes.normal)
    print(
        term_pos(menu_pos.top + 2, menu_pos.menu_y) + term_codes.bold + term_codes.yellow + "1. " + term_codes.normal +
        "Start Following a show (or activate via TVMaze Web)")
    print(
        term_pos(menu_pos.top + 3, menu_pos.menu_y) + term_codes.bold + term_codes.yellow + "2. " + term_codes.normal +
        "Start Skipping a followed Show (going forward)")
    print(
        term_pos(menu_pos.top + 4, menu_pos.menu_y) + term_codes.bold + term_codes.yellow + "3. " + term_codes.normal +
        "Un-follow a Show (erase history)")
    print(
        term_pos(menu_pos.top + 5, menu_pos.menu_y) + term_codes.bold + term_codes.yellow + "4. " +
        term_codes.normal + "Change a Show Download Option (API)")
    print(
        term_pos(menu_pos.top + 6, menu_pos.menu_y) + term_codes.bold + term_codes.yellow + "5. " + term_codes.normal +
        "New Shows to Review (" + str(num_list.num_newshows) + ")")
    
    print(
        term_pos(menu_pos.top + 2, menu_pos.menu_2y) + term_codes.bold + term_codes.yellow + "6. " + term_codes.normal +
        " Process Transmissions")
    print(
        term_pos(menu_pos.top + 3, menu_pos.menu_2y) + term_codes.bold + term_codes.yellow + "7. " + term_codes.normal +
        " Process Shows Updates")
    print(
        term_pos(menu_pos.top + 4, menu_pos.menu_2y) + term_codes.bold + term_codes.yellow + "8. " + term_codes.normal +
        " Process Episodes")
    print(
        term_pos(menu_pos.top + 5, menu_pos.menu_2y) + term_codes.bold + term_codes.yellow + "9. " + term_codes.normal +
        " Process Downloads")
    print(
        term_pos(menu_pos.top + 6, menu_pos.menu_2y) + term_codes.bold + term_codes.yellow + "10. " + term_codes.normal +
        "Process Statistics")
    print(term_pos(menu_pos.top + 7,
                   menu_pos.menu_2y) + term_codes.bold + term_codes.yellow + "11. " + term_codes.normal +
          "Process All (complete run)")
    print(term_pos(menu_pos.top + 8,
                   menu_pos.menu_2y) + term_codes.bold + term_codes.yellow + "12. " + term_codes.normal +
          "Clean up Plex directory structures")

    print(term_pos(menu_pos.top + 2,
                   menu_pos.menu_3y) + term_codes.bold + term_codes.yellow + "C (or c). " + term_codes.normal +
          "View Logs Files via Console")
    print(
        term_pos(menu_pos.top + 3,
                 menu_pos.menu_3y) + term_codes.bold + term_codes.yellow + "D (or d). " + term_codes.normal +
        "View Statistics Dashboard Webpage")
    print(term_pos(menu_pos.top + 4,
                   menu_pos.menu_3y) + term_codes.bold + term_codes.yellow + "H (or h). " + term_codes.normal +
          "TVMaze Help")
    '''
    print(term_pos(menu_pos.top + 6,
                   menu_pos.menu_3y) + term_codes.bold + term_codes.yellow + "I (or i). " + term_codes.normal +
          "Initialize TVMaze")
    '''
    print(
        term_pos(menu_pos.top + 8, menu_pos.menu_y) + term_codes.bold + term_codes.yellow + "F (or f). " +
        term_codes.normal + "Find a Shows via all download_options")
    
    if clear:
        print(term_pos(menu_pos.status_x, menu_pos.menu_y) + term_codes.red + term_codes.bold + "Status:",
              term_codes.normal)


def display_ou_menu(clear):
    if clear:
        print(term_codes.cl_scr)
    
    print(term_pos(menu_pos.top, menu_pos.menu_2y - 10) + term_codes.bold + term_codes.green +
          "TVMaze Other Utilities" +
          term_codes.red + " -> " + release.console_version + term_codes.normal)
    print(
        term_pos(menu_pos.top + 6, menu_pos.menu_y) + term_codes.bold + term_codes.yellow + "5. " + term_codes.normal +
        "View Shows to Review (" + str(num_list.num_newshows) + ")")
    
    print(
        term_pos(menu_pos.top + 2,
                 menu_pos.menu_2y) + term_codes.bold + term_codes.yellow + "6.  " + term_codes.normal +
        "View Full Process Log File")
    print(
        term_pos(menu_pos.top + 3,
                 menu_pos.menu_2y) + term_codes.bold + term_codes.yellow + "7.  " + term_codes.normal +
        "View Plex Cleanup Log File")
    print(
        term_pos(menu_pos.top + 4,
                 menu_pos.menu_2y) + term_codes.bold + term_codes.yellow + "8.  " + term_codes.normal +
        "View Download Log")
    print(
        term_pos(menu_pos.top + 2,
                 menu_pos.menu_3y) + term_codes.bold + term_codes.yellow + "S. (or s) " + term_codes.normal +
        "View Real-Time Statistics")
    print(
        term_pos(menu_pos.top + 3,
                 menu_pos.menu_3y) + term_codes.bold + term_codes.yellow + "H. (or h) " + term_codes.normal +
        "View Historical Statistics")
    print(
        term_pos(menu_pos.top + 5,
                 menu_pos.menu_3y) + term_codes.bold + term_codes.yellow + "D. (or d) " + term_codes.normal +
        "View Shows # by download_options")
    
    if clear:
        print(term_pos(menu_pos.status_x, menu_pos.menu_y) + term_codes.red + term_codes.bold + "Status:",
              term_codes.normal)


def get_menu_input():
    print(term_pos(menu_pos.input_x, menu_pos.menu_2y),
          end=term_codes.bold + term_codes.green + "Pick your Option (or q): " + term_codes.normal + term_codes.cl_eol)
    ans = input().lower()
    return ans


def get_ou_menu_input():
    print(term_pos(menu_pos.input_x, menu_pos.menu_2y),
          end=term_codes.bold + term_codes.green + "Pick your Option (or q): " + term_codes.normal + term_codes.cl_eol)
    ans = input().lower()
    return ans


def get_show_input(x, y):
    print(term_pos(x, y + 10) + term_codes.cl_eol)
    print(term_pos(x, y),
          end=term_codes.bold + "Which Show (id or name or q): " + term_codes.normal + term_codes.cl_eol)
    show = input()
    return show


def display_recs(records, header, extra=0):
    print(term_pos(menu_pos.status_x, menu_pos.status_y) + header + term_codes.cl_eol)
    if header == "download_options Available":
        y = menu_pos.menu_2y
    else:
        y = menu_pos.menu_y
    idx = 1
    for rec in records:
        print(term_pos(menu_pos.sub_screen_x + idx + extra, y) + str(idx) + ". " + str(rec) +
              term_codes.cl_eol)
        idx = idx + 1


def process_ou_menu(inp):
    if inp == "5":
        display_recs(num_list.new_list, "New Shows to Review")
    elif inp == "6":
        print(term_pos(menu_pos.status_x, menu_pos.status_y), "Opening Console" + term_codes.cl_eol)
        print()
        log_file = '/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/Logs/30M-Process.log'
        log_path = 'open -a /System/Applications/Utilities/Console.app ' + log_file
        os.system(log_path)
    elif inp == "8":
        display_ou_menu(True)
        print(term_pos(menu_pos.status_x, menu_pos.status_y), "Viewing Transmission Log" + term_codes.cl_eol)
        print()
        subprocess.call("cat /Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/Apps/Logs/LogPlexThemProgram.txt ",
                        shell=True)
    elif inp == "8c":
        display_ou_menu(True)
        print(term_pos(menu_pos.status_x, menu_pos.status_y), "Cleaning Transmission log" + term_codes.cl_eol)
        print()
        subprocess.call("echo "" "
                        ">/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/Apps/Logs/LogPlexThemProgram.txt ",
                        shell=True)
    elif inp == "7":
        display_ou_menu(True)
        print(term_pos(menu_pos.status_x, menu_pos.status_y), "Viewing Plex Cleanup Log" + term_codes.cl_eol)
        print()
        subprocess.call("cat /Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/Apps/Logs/Clean_SRTs_log.txt ",
                        shell=True)
    elif inp == "7c":
        display_ou_menu(True)
        print(term_pos(menu_pos.status_x, menu_pos.status_y), "Cleaning Plex Cleanup Log" + term_codes.cl_eol)
        print()
        subprocess.call("echo "" >/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/Apps/Logs/Clean_SRTs_log.txt ",
                        shell=True)
    elif inp == "s":
        display_ou_menu(True)
        print(term_pos(menu_pos.status_x, menu_pos.status_y), "Displaying the current Statistics" + term_codes.cl_eol)
        subprocess.call(" python3 statistics.py -d", shell=True)
    elif inp == "h":
        display_ou_menu(True)
        print(term_pos(menu_pos.status_x, menu_pos.status_y), "Displaying the historical Statistics" +
              term_codes.cl_eol)
        subprocess.call(" python3 statistics.py -v", shell=True)
    elif inp == "d":
        display_ou_menu(True)
        print(term_pos(menu_pos.status_x, menu_pos.status_y), "Showing the Downloader count of shows" +
              term_codes.cl_eol)
        counts = count_by_download_options()
        print(term_pos(menu_pos.status_x + 2, menu_pos.menu_2y) + "No Downloader assigned     : " +
              rjust_str(str(counts[0]), 5) + term_codes.cl_eol)
        print(term_pos(menu_pos.status_x + 3, menu_pos.menu_2y) + "rarbgAPI assigned          : " +
              rjust_str(str(counts[1]), 5) + term_codes.cl_eol)
        print(term_pos(menu_pos.status_x + 4, menu_pos.menu_2y) + "ShowRSS assigned           : " +
              rjust_str(str(counts[4]), 5) + term_codes.cl_eol)
        print(term_pos(menu_pos.status_x + 5, menu_pos.menu_2y) + "Followed Shows in Skip Mode: " +
              rjust_str(str(counts[5]), 5) + term_codes.cl_eol)
        print(term_pos(menu_pos.status_x + 6, menu_pos.menu_2y) + "rarbg (lookup) assigned    : " +
              rjust_str(str(counts[2]), 5) + term_codes.cl_eol)
        print(term_pos(menu_pos.status_x + 7, menu_pos.menu_2y) + "eztvAPI assigned           : " +
              rjust_str(str(counts[6]), 5) + term_codes.cl_eol)
        print(term_pos(menu_pos.status_x + 8, menu_pos.menu_2y) + "eztv assigned              :" +
              rjust_str(str(counts[7]), 6) + term_codes.cl_eol)
        print(term_pos(menu_pos.status_x + 9, menu_pos.menu_2y) + "magnetdl assigned          : " +
              rjust_str(str(counts[8]), 5) + term_codes.cl_eol)
        print(term_pos(menu_pos.status_x + 10, menu_pos.menu_2y) + "torrentfunk assigned       : " +
              rjust_str(str(counts[9]), 5) + term_codes.cl_eol)
    elif inp == "r" or inp == "":
        display_ou_menu(True)
        print(term_pos(menu_pos.status_x, menu_pos.status_y), "Refreshed" + term_codes.cl_eol)
    else:
        print(term_pos(menu_pos.status_x, menu_pos.status_y) + term_codes.red +
              "Option does not exist" + term_codes.normal + term_codes.cl_eol)
        return False


def get_which_show(x, y):
    print(term_pos(x, y + 11) + term_codes.cl_eol)
    print(term_pos(x, y),
          end=term_codes.bold + "Select which show (seq# or q): " + term_codes.normal + term_codes.cl_eol)
    show = input()
    return show


def back_to_menu(blanks):
    ans = input(term_pos(menu_pos.input_x, menu_pos.menu_2y) + term_codes.green +
                "Back to Menu or Quit - Hit 'Enter' (or q): " + term_codes.normal + term_codes.cl_eol).lower()
    if ans == "q":
        print()
        quit()
    else:
        print(term_pos(menu_pos.status_x, menu_pos.status_y) + term_codes.cl_eol)
        idx = 1
        while idx <= blanks:
            print(term_pos((menu_pos.status_x + idx), 0) + term_codes.cl_eol)
            idx = idx + 1


def tvm_follow(fl, si):
    info_api = 'https://api.tvmaze.com/v1/user/follows/shows/' + str(si)
    if fl == "F":
        shows = requests.put(info_api,
                             headers={'Authorization':
                                      'Basic RGlja0tsdWlzOlRUSFlfQ2hIeUF5SU1fV1ZZRmUwcDhrWTkxTkE1WUNH'})
        if shows.status_code != 200:
            print("Error trying to follow show:", si, shows.status_code)
            return False
    elif fl == "U":
        shows = requests.delete(info_api,
                                headers={'Authorization':
                                         'Basic RGlja0tsdWlzOlRUSFlfQ2hIeUF5SU1fV1ZZRmUwcDhrWTkxTkE1WUNH'})
        if shows.status_code != 200 and shows.status_code != 404:
            print("Error trying to un-follow show:", si, shows.status_code)
            return False
    return True


def find_via_showid(si):
    to_download = execute_sql(sqltype='Fetch', sql=f"SELECT * from shows WHERE `showid` = {si};")
    if not to_download:
        return False
    if len(to_download) != 1:
        return False
    return to_download


def find_via_showname(sn):
    to_download = execute_sql(sqltype='Fetch', sql=f"SELECT * from shows WHERE `showname` like '{sn}';")
    if not to_download:
        return False
    if len(to_download) == 0:
        return False
    return to_download


def get_alt_showname(si):
    alt_showname = execute_sql(sqltype='Fetch', sql=f"SELECT * from shows WHERE `showid` like {si};")
    if not alt_showname:
        return False
    if len(alt_showname) == 0:
        return False
    return alt_showname[0][0]


def follow_a_show(si):
    succe = tvm_follow("F", si)
    if not succe:
        print("TVMaze could not follow Shows", si, succe)
        return False
    return True


def skip_a_followed_show(si):
    # First set the all-show info to Skipped
    result = execute_sql(sqltype='Commit', sql=f"UPDATE shows SET download = 'Skip' WHERE `showid` = {si};")
    if not result:
        return False
    # Second set all none watched shows to Skipped in the episode table
    # Todo set the shows episodes to Skip on TVMaze
    # Get lis of all NULL or Downloaded eps
    # Iterate and update TVMaze to Skip
    return True


def un_follow_a_show(si):
    # Let TVMaze know we are un-following the show
    suc = tvm_follow("U", si)
    if not suc:
        print("TVMaze could not un-follow Shows", si)
        return False
    # First set the all-show info to Skipped
    result = execute_sql(sqltype='Commit', sql=f"UPDATE shows "
                                               f"SET status = 'Skipped', download = Null "
                                               f"WHERE showid = {si}")
    if not result:
        print(f'Update of show {si} did not work and did not try to delete the episodes')
        return False
    # then delete the show form the Episodes Table
    result = execute_sql(sqltype='Commit', sql=f'DELETE from episodes WHERE showid = {si}')
    if not result:
        print(f'Delete of the episodes did not work for show {si}')
    return True


def change_download_for_a_show(si, dled):
    result = execute_sql(sqltype='Commit', sql=f"UPDATE shows SET download = '{dled}' WHERE showid = {si}")
    if not result:
        print(f'Update to change the download to {dled} for show {si} did not work')
        return False
    return True


def get_show(message):
    status_txt = message + term_codes.cl_eol
    print(term_pos(menu_pos.status_x, menu_pos.status_y), status_txt)
    while True:
        show_in = get_show_input(menu_pos.sub_screen_x, menu_pos.menu_y)
        if show_in == 'q':
            clear_subscreen(5)
            return "Quit", 0
        if show_in.isdigit():
            found_shows = find_via_showid(int(show_in))
        else:
            found_shows = find_via_showname(show_in)
        if not found_shows:
            print(term_pos(menu_pos.sub_screen_x, menu_pos.menu_3y) + term_codes.red +
                  "Could not find the requested show" + term_codes.normal + term_codes.cl_eol)
            return "Failed", 0
        rec = 0
        found_txt = message + term_codes.cl_eol
        print(term_pos(menu_pos.status_x, menu_pos.status_y), found_txt)
        num_fs = len(found_shows)
        for found_show in found_shows:
            if not found_show[5]:
                premiered = ""
            else:
                premiered = found_show[5]
            tvm_link = "  https://www.tvmaze.com/shows/" + str(found_show[0])
            feedback_txt = "Showid: " + ljust_str(found_show[0], 5) + \
                           "   Showname: " + ljust_str(found_show[1], 45) + \
                           term_codes.blue + "   Downloader: " + ljust_str(str(found_show[16]), 12) + \
                           "   Show Status: " + ljust_str(found_show[4], 17) + \
                           "   Premiered: " + premiered + "   My Status: " + ljust_str(found_show[15], 9) \
                           + term_codes.normal + "   " + tvm_link
            if num_fs <= 3:
                follow_str = 'open -a safari ' + tvm_link
                os.system(follow_str)
            if num_fs < 10:
                rj = 1
            else:
                rj = 2
            print(term_pos(menu_pos.sub_screen_x + rec + 1, menu_pos.menu_2y) +
                  rjust_str(rec, rj) + ": " + feedback_txt)
            rec = rec + 1
        which_show = get_which_show(menu_pos.sub_screen_x, menu_pos.menu_y)
        if which_show == 'q':
            clear_shows(rec + 1)
            return "Quit", 0
        else:
            if which_show.isdigit() and int(which_show) < len(found_shows):
                status_txt = message + " show: " + str(found_shows[int(which_show)][0]) + term_codes.cl_eol
                print(term_pos(menu_pos.status_x, menu_pos.status_y), status_txt)
                return found_shows[int(which_show)][0], len(found_shows), found_show[18]


def get_download_selected(dls):
    recs = len(dls)
    print(term_pos(menu_pos.sub_screen_x, menu_pos.menu_2y - 10) + term_codes.cl_eol)
    print(term_pos(menu_pos.sub_screen_x, menu_pos.menu_2y - 10),
          end=term_codes.bold + "Which Downloader (id or q): " + term_codes.normal + term_codes.cl_eol)
    show = input().lower()
    if show == "q":
        return "Quit"
    if show.isnumeric():
        show = int(show)
    if 0 < show <= recs:
        return dls[show - 1][0]
    else:
        return "Quit"


'''
    Main program
    First get all the supporting lists we use
'''
display_menu(True)
loop = True
while loop:
    cons_in = get_menu_input()
    cl_screen = True
    if cons_in == 'q':
        print(term_pos(menu_pos.status_x, menu_pos.status_y), "Quit" + term_codes.cl_eol)
        print(term_pos(menu_pos.status_x + 1, 0))
        break
    elif cons_in == "1":
        display_menu(True)
        print(term_pos(menu_pos.status_x, menu_pos.status_y), "Start Following a show" + term_codes.cl_eol)
        print()
        showinfo = get_show("Follow a Show")
        shownum = showinfo[0]
        showcount = showinfo[1]
        if shownum != "Quit" and shownum != "Failed":
            success = follow_a_show(shownum)
            if success:
                print(term_pos(menu_pos.status_x, menu_pos.status_y),
                      "Now Following show: " + str(shownum) + term_codes.cl_eol)
                cl_screen = False
            else:
                print(term_pos(menu_pos.status_x, menu_pos.status_y),
                      "Error occurred while trying to follow show: " + str(shownum) + term_codes.cl_eol)
                cl_screen = False
        else:
            print(term_pos(menu_pos.status_x, menu_pos.status_y), "No Show selected to follow " + term_codes.cl_eol)
            print(term_pos(menu_pos.status_x + 2, menu_pos.menu_y) + term_codes.cl_eol)
            cl_screen = False
    elif cons_in == "2":
        display_menu(True)
        print(term_pos(menu_pos.status_x, menu_pos.status_y), "Skip a show" + term_codes.cl_eol)
        print()
        showinfo = get_show("Skip a Show")
        shownum = showinfo[0]
        showcount = showinfo[1]
        if shownum != "Quit" and shownum != "Failed":
            print(term_pos(menu_pos.status_x, menu_pos.status_y),
                  "Process the Skipping for show: " + str(shownum) + term_codes.cl_eol)
            execute_sql(sqltype='Commit', sql=f'UPDATE shows SET download = "Skip" WHERE `showid` = {shownum}')
            cl_screen = False
        else:
            print(term_pos(menu_pos.status_x, menu_pos.status_y), "No Show selected to skip " + term_codes.cl_eol)
            print(term_pos(menu_pos.status_x + 2, menu_pos.menu_y) + term_codes.cl_eol)
            cl_screen = False
    elif cons_in == "3":
        display_menu(True)
        print(term_pos(menu_pos.status_x, menu_pos.status_y), "Un-Follow a show" + term_codes.cl_eol)
        print()
        showinfo = get_show("Un-follow a Show")
        shownum = showinfo[0]
        showcount = showinfo[1]
        if showinfo == "q":
            shownum = "Quit"
        if shownum != "Quit" and shownum != "Failed":
            print(term_pos(menu_pos.status_x, menu_pos.status_y),
                  "Process the Un-Follow a show: " + str(shownum) + term_codes.cl_eol)
            success = un_follow_a_show(shownum)
            if success:
                print(term_pos(menu_pos.status_x, menu_pos.status_y),
                      "Show un-followed: " + str(shownum) + term_codes.cl_eol)
                cl_screen = False
            else:
                print(term_pos(menu_pos.status_x, menu_pos.status_y),
                      "Error occurred while un-following show: " + str(shownum) + term_codes.cl_eol)
                cl_screen = False
        else:
            print(term_pos(menu_pos.status_x, menu_pos.status_y), "No Show selected to un-follow " + term_codes.cl_eol)
            print(term_pos(menu_pos.status_x + 2, menu_pos.menu_y) + term_codes.cl_eol)
            cl_screen = False
    elif cons_in == "4":
        display_menu(True)
        print(term_pos(menu_pos.status_x, menu_pos.status_y), "Change Download for a Show" + term_codes.cl_eol)
        print()
        showinfo = get_show("Change Download for a Show")
        shownum = showinfo[0]
        showcount = showinfo[1]
        if showinfo == 'q':
            shownum = "Quit"
        if shownum != "Quit" and shownum != "Failed":
            print(term_pos(menu_pos.status_x, menu_pos.status_y),
                  "Process the Download Change for show: " + str(shownum) + term_codes.cl_eol)
            download_options = get_download_options()
            display_recs(download_options, "download_options Available", showcount + 1)
            downloader = get_download_selected(download_options)
            if downloader != "Quit":
                success = change_download_for_a_show(shownum, downloader)
            else:
                success = False
            if success:
                print(term_pos(menu_pos.status_x, menu_pos.status_y),
                      "Download Changed for show: " + str(shownum) + term_codes.cl_eol)
                cl_screen = False
            else:
                print(term_pos(menu_pos.status_x, menu_pos.status_y),
                      "Error occurred while changing download for show: " + str(shownum) + term_codes.cl_eol)
                cl_screen = False
        else:
            print(term_pos(menu_pos.status_x, menu_pos.status_y), "No Show selected for download change" +
                  term_codes.cl_eol)
            print(term_pos(menu_pos.status_x + 2, menu_pos.menu_y) + term_codes.cl_eol)
            cl_screen = False
    elif cons_in == "f":
        display_menu(True)
        print(term_pos(menu_pos.status_x, menu_pos.status_y), "Find a show via all download_options" + term_codes.cl_eol)
        print()
        showinfo = get_show("Find a Show")
        shownum = showinfo[0]
        showcount = showinfo[1]
        if showinfo == 'q':
            shownum = ' Quit'
        if shownum != 'Quit' and shownum != 'Failed':
            dls = get_download_options(True)
            for dl in dls:
                if not dl[2]:
                    sfx = ''
                else:
                    sfx = str(dl[2])
                if "magnetdl" in dl[1]:
                    dl_str = dl[1] + str(showinfo[2][0]).lower() + "/"
                else:
                    dl_str = dl[1]
                dl_link = dl_str + str(showinfo[2]).replace(' ', dl[3]).lower() + sfx
                follow_str = 'open -a safari ' + dl_link
                os.system(follow_str)
    elif cons_in == "11":
        display_menu(True)
        print(term_pos(menu_pos.status_x, menu_pos.status_y), "Complete TVMaze Update Run" + term_codes.cl_eol)
        print()
        subprocess.call(" /Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/Scripts/tvm_process.sh",
                        shell=True)
        cl_screen = False
    elif cons_in == "5":
        display_menu(True)
        print(term_pos(menu_pos.status_x, menu_pos.status_y), "New Shows to Review" + term_codes.cl_eol)
        print()
        subprocess.call(" python3 actions.py -r", shell=True)
        cl_screen = False
    elif cons_in == "6":
        display_menu(True)
        print(term_pos(menu_pos.status_x, menu_pos.status_y), "New Shows to Review" + term_codes.cl_eol)
        print()
        subprocess.call(" python3 transmission.py", shell=True)
        cl_screen = False
    elif cons_in == "7":
        display_menu(True)
        print(term_pos(menu_pos.status_x, menu_pos.status_y), "Process Shows" + term_codes.cl_eol)
        print()
        subprocess.call(" python3 shows.py -u", shell=True)
        cl_screen = False
    elif cons_in == "8":
        display_menu(True)
        print(term_pos(menu_pos.status_x, menu_pos.status_y), "Process Episodes" + term_codes.cl_eol)
        print()
        subprocess.call(" python3 episodes.py", shell=True)
        cl_screen = False
    elif cons_in == "9":
        display_menu(True)
        print(term_pos(menu_pos.status_x, menu_pos.status_y), "Process Downloads" + term_codes.cl_eol)
        print()
        subprocess.call(" python3 actions.py -d", shell=True)
        cl_screen = False
    elif cons_in == "10":
        display_menu(True)
        print(term_pos(menu_pos.status_x, menu_pos.status_y), "Process Statistics" + term_codes.cl_eol)
        print()
        subprocess.call(" python3 statistics.py -s", shell=True)
        cl_screen = False
        subprocess.call(" python3 actions.py -d", shell=True)
    elif cons_in == "12":
        display_menu(True)
        print(term_pos(menu_pos.status_x, menu_pos.status_y), "Clean up leftovers in Plex" + term_codes.cl_eol)
        print()
        cl_screen = False
        subprocess.call(" /Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/Scripts/plex_cleanup.sh ",
                        shell=True)
    elif cons_in == "h":
        cl_screen = False
        print(term_pos(menu_pos.status_x, menu_pos.status_y),
              "Started Safari with the TVMaze Help Documentation" +
              term_codes.cl_eol)
        subprocess.call(" open -a safari  /Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/README.pdf",
                        shell=True)
    elif cons_in == "r" or cons_in == "":
        display_menu(True)
        print(term_pos(menu_pos.status_x, menu_pos.status_y), "Refreshed" + term_codes.cl_eol)
        print()
    elif cons_in == "c":
        print(term_pos(menu_pos.status_x, menu_pos.status_y), "Opening Consoles" + term_codes.cl_eol)
        print()
        log_file = '/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/Logs/30M-Process.log'
        log_path = 'open -a /System/Applications/Utilities/Console.app ' + log_file
        os.system(log_path)
        log_file = '/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/Logs/Swift_Rep.log'
        log_path = 'open -a /System/Applications/Utilities/Console.app ' + log_file
        os.system(log_path)
        log_file = '/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/Logs/Plex-Cleanup.log'
        log_path = 'open -a /System/Applications/Utilities/Console.app ' + log_file
        os.system(log_path)
        log_file = '/Volumes/HD-Data-CA-Server/PlexMedia/PlexProcessing/TVMaze/Logs/Transmission.log'
        log_path = 'open -a /System/Applications/Utilities/Console.app ' + log_file
        os.system(log_path)
    elif cons_in == "d":
        display_menu(True)
        cl_screen = True
        print(term_pos(menu_pos.status_x, menu_pos.status_y), "Starting Statistics Webserver (use CTLR-C to stop"
              + term_codes.cl_eol)
        print()
        follow_str = 'open -a safari http://127.0.0.1:8050'
        os.system(follow_str)
        try:
            subprocess.call(" python3 visualize.py", shell=True)
        except KeyboardInterrupt:
            display_menu(True)
            pass
    elif cons_in == "o":
        ou_loop = True
        cl_screen = True
        while ou_loop:
            display_ou_menu(cl_screen)
            cl_screen = False
            ou_in = get_ou_menu_input()
            if ou_in == "q":
                ou_loop = False
            else:
                process_ou_menu(ou_in)
        display_menu(True)
    else:
        cl_screen = False
        print(term_pos(menu_pos.status_x, menu_pos.status_y) + term_codes.red,
              "Not yet implemented" + term_codes.cl_eol)
    
    del sys.modules['tvm_lib']
    from tvm_lib import num_list
