"""
    Logging Library for TVM-Management
"""

import os
import time

from Libraries.tvm_db import get_tvmaze_info


class logging:
    def __init__(self, env=False, caller='', filename='Unknown'):
        """
                        Initialization
        :param env:     Anything but 'Prod' (is default) will put the log file in the test environment mode
                          All paths come from the key_values in the DB
        :param caller   The program opening the log file
        :param filename The filename to use
        """
        if not env:
            if 'Pycharm' in os.getcwd():
                env = 'Test'
            else:
                env = 'Prod'
        
        sp = get_tvmaze_info('path_scripts')
        if env == 'Prod':
            lp = get_tvmaze_info('path_prod_logs')
            ap = get_tvmaze_info('path_prod_apps')
        else:
            lp = get_tvmaze_info('path_tst_logs')
            ap = get_tvmaze_info('path_tst_apps')
        
        self.log_path = lp
        self.app_path = ap
        self.scr_path = sp
        self.logfile = 'NotSet'
        self.caller = caller
        self.filename = filename
        self.file_status = False
        self.content = []
    
    def open(self, mode='a+', read=False):
        """
                    Open the log file
        :param file:    The filename (is appended with .log automatically)
        :param mode:    The open mode for the file, default = a+
        :param read:    Also read file into log file .content
        :return:
        """
        self.logfile = open(f'{self.log_path}{self.filename}.log', mode)
        self.file_status = True
        if read:
            self.logfile.read()
        
    def close(self):
        """
                    Close the file
        :return:
        """
        if self.file_status:
            self.logfile.close()
            self.file_status = False
    
    def write(self, message='', level=1, read=False):
        """
                    Write the message to the log file
        :param message:     Text to be written
        :param level:       Information Level Indicator
        :param read:        Also read file into log file .content
        :return:
        """
        message = f"{self.caller} > Level {level} > {time.strftime('%D %T')}: {message}\n"
        if not self.file_status:
            self.open(mode='a+')
            self.logfile.write(message)
            self.close()
        else:
            self.logfile.write(message)
        if read:
            self.read()
        
    def empty(self):
        """
                    Empty the log file
        :return:
        """
        if self.file_status:
            self.logfile.close()
        self.open(mode='w+')
        self.logfile.close()
        self.file_status = False
        
    def read(self):
        """
                    Read the whole log file
        :return:        Note: all content pushed into log file .content
        """
        self.close()
        self.open(mode='r+')
        self.content = self.logfile.read()
        self.close()
        

