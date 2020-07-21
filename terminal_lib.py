import sys
from tvm_lib import get_tvmaze_info


def check_cli_args(ltc):
    clis = sys.argv
    fl = {}
    for tc in ltc:
        fl[tc] = False
        for cli in clis:
            if cli == tc:
                fl[tc] = True
    return fl


class term_codes:
    cl_eol = "\033[K"
    cl_scr = "\033[2J\033[1;1f"
    blue = '\033[34m'
    bold = '\033[1m'
    green = '\033[32m'
    normal = '\033[0m'
    red = '\033[31m'
    yellow = '\033[33m'


def term_pos(x, y):
    enc = "\033[" + str(x) + ";" + str(y) + "H"
    return enc


def rjust_str(instr, size):
    return str(instr).rjust(size)


def ljust_str(instr, size):
    return str(instr).ljust(size)


class menu_pos:
    top = int(get_tvmaze_info('"mtop"'))
    menu_y = int(get_tvmaze_info('"mmenu_y"'))
    menu_2y = int(get_tvmaze_info('"mmenu_2y"'))
    menu_3y = int(get_tvmaze_info('"mmenu_3y"'))
    status_y = int(get_tvmaze_info('"mstatus_y"'))
    input_x = top + int(get_tvmaze_info('"minput_x"'))
    status_x = input_x + int(get_tvmaze_info('"mstatus_x"'))
    sub_screen_x = status_x + int(get_tvmaze_info('"msub_screen_x"'))
