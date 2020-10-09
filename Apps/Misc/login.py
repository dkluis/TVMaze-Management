from dearpygui.dearpygui import *
from dearpygui.wrappers import *


def func_recursively_show_main(container):
    for item in get_item_children(container):
        if get_item_children(item):
            show_item(item)
            func_recursively_show_main(item)
        else:
            show_item(item)


def func_login(sender, data):
    if get_value('password') == 'password':
        delete_item('Login Window')
        func_recursively_show_main('MainWindow')


def window_login():
    with window('Login Window', title_bar=False, movable=False, autosize=True, resizable=False):
        add_input_text('password', hint='password is password', password=True)
        add_button('Submit', callback=func_login)


def window_main():
    with menu_bar('menu bar'):
        with menu('menu 1'):
            add_menu_item('menu item')
    add_text('You are now logged in')
    hide_item('MainWindow', children_only=True)


window_main()
window_login()
start_dearpygui()