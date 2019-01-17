"""
XML Glozz project
------------------------------------------------------------

This module contains only one static class to log information.

"""

#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------

# Standard library
import datetime
import time

#-------------------------------------------------------------------------------
# Tool
#-------------------------------------------------------------------------------

class Log:
    """A simple logger class"""

    start_time = None
    
    def __init__(self):
        Log.error('This class is static : no instanciation allowed.')

    @staticmethod
    def start():
        Log.start_time = datetime.datetime.now()
        Log.info('Program has started')
    
    @staticmethod
    def get_timestamp() -> str:
        d = datetime.datetime.now()
        return d.strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def error(msg : str, code : int = 1):
        print('[ERROR]', Log.get_timestamp(), msg)
        exit(code)

    @staticmethod
    def warn(msg : str):
        print('[WARN] ', Log.get_timestamp(), msg)

    @staticmethod
    def info(msg : str):
        print('[INFO] ', Log.get_timestamp(), msg)

    @staticmethod
    def end():
        Log.info('Program has ended. Duration : ' + str(datetime.datetime.now() - Log.start_time))
    
#-------------------------------------------------------------------------------
# Main (unit tests)
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    Log.start()
    Log.info('info message')
    Log.warn('warn message')
    Log.end()
    Log.error('error message + ending')
