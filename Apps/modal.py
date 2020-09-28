from dearpygui.dearpygui import *
from dearpygui.wrappers import *

add_button("Login")
with popup("Login", 'Login Popup', modal=True):
    add_input_text("User Name")
    add_input_text("Password", password=True)
    add_button("Submit", callback="try_login")

add_button('Another button')


def try_login(sender, data):
    log_debug(get_value("User Name"))
    log_debug(get_value("Password"))
    close_popup()


start_dearpygui()