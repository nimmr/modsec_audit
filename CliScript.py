
from __future__ import print_function
import Benchmarking
import os
import sys

__author__ = 'tl'


class CliScript(object):

    _verbose = False
    _color_terminal = False
    _gracefullyEnded = False
    _counters =  dict()
    timers = None


    COLOR_STANDARD	= "\033[m"
    COLOR_RED		= "\033[31m"
    COLOR_GREEN		= "\033[1;32m"
    COLOR_BLUE		= "\033[1;34m"
    COLOR_YELLOW	= "\033[1;33m"

    LOG_EMERG		= 0
    LOG_ALERT		= 1
    LOG_CRIT		= 2
    LOG_ERROR		= 3
    LOG_WARN		= 4
    LOG_NOTICE		= 5
    LOG_INFO		= 6
    LOG_DEBUG		= 7

    def __init__(self, verbose=False):
        """

        :param verbose: bool
        """

        self.timers = Benchmarking.Benchmarking()
        self._verbose = verbose
        self.exit_on_end = True


        if os.name == 'posix':
            self._color_terminal = True


    def end(self):
        """
        If verbose, print timers and counters, and then ends the script
        """

        if self._gracefullyEnded is True:
            return None

        self.timers.end_timers()

        if self._verbose is True:

            self.timers.print_timers()

            if len(self._counters):
                print('Counters:')
                for key, val in self._counters.items():
                    print('\t{0:<30} {1:>12}'.format(key, val))

            self.print_color('Program ended', self.COLOR_BLUE)

        self._gracefullyEnded = True

        if self.exit_on_end:
            sys.exit(0)


    def set_exit_on_end(self, val):
        """
        set to False to stop end() from exit(0)'ing
        :param val: bool
        """

        if not val is True and val is not False:
            raise Exception('value must be boolean')

        self.exit_on_end = val

    def print_color(self, msg, color):
        """
        Prints a message in color, if supported by the terminal

        :param msg: string
        :param color: string
        """

        if self._color_terminal:
            print(color, end='')

        print(msg)

        if self._color_terminal:
            print(self.COLOR_STANDARD, end='')


    def log(self, level, msg):
        """
        Must be implemented in subclass

        :param level: int
        :param msg: string
        """
        self.print_color('Logging not implemented!', self.COLOR_RED)
        print(msg)


    def get_counter(self, key):
        """
        Get a previously created counter

        :param key: string
        """
        if not key in self._counters:
            raise Exception('The key {} dosn\'t exist in counters'.format(key))

        return self._counters[key]


    def counter(self, key, val=1):
        """
        Create or increment a counter

        :param key: string
        :param val: int
        """

        if key in self._counters:
            self._counters[key] += val
        else:
            self._counters[key] = val