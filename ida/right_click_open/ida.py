# -*- coding: utf-8 -*-

#
# Use to open ida without checking the file bits manually.
# Test on Windows 10 1909 and Python3.8
# @author: ty.
# Usage:
# 1. copy ida.py into ida's root folder 
# 2. run ida.py with the following command:
# ```python ida.py --install```

import pefile
import sys
import os
import ctypes

SEE_MASK_NO_CONSOLE = 0x00008000
SEE_MASK_NOCLOSE_PROCESS = 0x00000040
class IDA(object):
    """IDA object"""

    _ida32_path = ""
    _ida64_path = ""
    
    def __init__(self, file_path):
        """
        @parm file_path: file path
        """
        self._file_path = None
        if os.path.exists(file_path):
            self._file_path = os.path.abspath(file_path)
            try:
                self._pe = pefile.PE(self._file_path)
            except:
                self._pe = None
            
    
    def _get_ida_path(self):
        """get 'ida.exe' and 'ida64.exe' path
        @return: True or False 
        """
        ida_base = os.path.split(os.path.abspath(__file__))[0]
        self._ida32_path = os.path.join(ida_base, 'ida.exe')
        self._ida64_path = os.path.join(ida_base, 'ida64.exe')
        self._idabat_path = os.path.join(ida_base, 'ida.bat')

        # wirte ida.bat
        if not os.path.exists(self._idabat_path):
            f = open(self._idabat_path, 'w')
            f.write('@echo off\n')
            f.write('if %2 == 32 start ' + self._ida32_path +' %1\n')
            f.write('if %2 == 64 start ' + self._ida64_path +' %1\n')
            f.close()

        # check file exists
        if os.path.exists(self._ida32_path) \
            and os.path.exists(self._ida64_path):
            return True

        return False

    def _is_file_32(self):
        """Check if the file is 32
        @return: True or False 
        """
        if self._pe is None:
            ext = os.path.splitext(self._file_path)[1]
            if ext == '.idb':
                return True
            elif ext == '.i64':
                return False
            else:
                # default use 32 bit
                return True
        if hex(self._pe.FILE_HEADER.Machine) == '0x14c':
            return True
        return False

    def run(self):
        """Run ida"""
        if not self._file_path:
            return
        if not self._get_ida_path():
            return
        if self._is_file_32():
            os.system(self._idabat_path + ' ' + self._file_path + ' 32')
        else:
            os.system(self._idabat_path + ' ' + self._file_path + ' 64')

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def regedit():
    #key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, r"")
    #print(is_admin())
    if is_admin():
        print('get')
    else:
        ctypes.windll.shell32.ShellExecuteW(lpVerb = 'runas', 
                                            lpFile = sys.executable,
                                            slpParameters = sys.argv,
                                            fMask = SEE_MASK_NO_CONSOLE|SEE_MASK_NOCLOSE_PROCESS)
        print('success')

def install():
    print('[+] install start')
    regedit()

def update():
    pass

def ida_help():
    print('Usage:')
    print('python ida.py []')
    print('--install')
    print('--update')
    print('--help')

if __name__ == "__main__":
    argc = len(sys.argv)
    for arg in sys.argv:
        print(arg)
    if argc == 1:
        ida_help()
    elif sys.argv[1] == '--install':
        install()
    elif sys.argv[1] == '--update':
        update()
    else:
        IDA(sys.argv[1]).run()