from typing import Type, Dict, Union


class part:
    def __init__(self):
        self.__data = None
        self.__initialized = False
        self.__data_structure = {
            'showid': int,
            'showname': str
        }
        self._data = self.__data_structure
        
        self.info = None
 
    def read(self, showid: int = 0, showname: str = '') -> bool:
        """
                Get all information about a part
                Return True if found otherwise return False
                if found:
                    part.info is dictionary with all fields filled
        :param showid:      if filled in use it to find the part
        :param showname:    if showid is not filled in use showname and
                                also look in the alt_showname field
        :return:            True if found
                            False if not found
        """
        self.__find(showid, showname)
        if self.__initialized:
            self.info = self.__data
            return True
        else:
            self.info = self.__data_structure
            return False
    
    def write(self):
        pass
    
    def delete(self):
        pass
    
    def __fix_showname(self, showid):
        pass
    
    def __find(self, showid, showname):
        if showid != 0:
            self.__dict()
        elif showname != '':
            self.__dict()
        else:
            self.__exist

    def __dict(self):
        pass
