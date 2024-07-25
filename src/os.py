import uos as os
from uos import *


class path:

    @staticmethod
    def exists(filename):
        try:
            os.stat(filename)
            return True
        except OSError:
            return False

    @staticmethod
    def isdir(filename):
        try:
            return (os.stat(filename)[0] & 0x4000) != 0
        except OSError:
            return False

    @staticmethod
    def isfile(filename):
        try:
            return (os.stat(filename)[0] & 0x4000) == 0
        except OSError:
            return False
