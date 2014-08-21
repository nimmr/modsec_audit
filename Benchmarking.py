from __future__ import print_function
try:
    from collections import OrderedDict
except:
    from ordereddict import OrderedDict

__author__ = 'Tim Lund <code@nimmr.dk>'

import time

#
# Far from done. I need to port some more code from my PHP version.
#
class Benchmarking:


    def __init__(self):
        self.timers = dict()


    def timer_exists(self, key):
        if not key in self.timers:
            raise Exception('Timer with name "{0}" does not exist'.format(key))


    def start_timer(self, key):
        if not key in self.timers:
            self.timers[key] = dict()

        self.timers[key]['start'] = time.time()


    def end_timer(self, key):
        self.timer_exists(key)

        if not 'start' in self.timers[key]:
            return

        val = self.timers[key]['total'] if 'total' in self.timers[key] else 0

        self.timers[key]['total'] = time.time() - self.timers[key]['start'] + val

        del self.timers[key]['start']


    def end_timers(self):

        for key in self.timers:
            self.end_timer(key)


    def toggle_timer(self, key):

        if not key in self.timers:
            self.start_timer(key)
        else:
            if 'start' in self.timers[key]:
                self.end_timer(key)
            else:
                self.start_timer(key)


    def get_timer(self, key):

        self.timer_exists(key)

        if not 'total' in self.timers[key]:
            self.end_timer(key)

        return self.timers[key]['total']


    def get_timers(self):
        """
        :return: dict of (str, float)
        """

        r = {}
        for key in self.timers:
            r[key] = self.get_timer(key)

        r = OrderedDict(sorted(r.items(), key=lambda x: x[1], reverse=True))

        return r

    def print_timers(self):

        print('Timers:')

        for key, val in self.get_timers().items():
            print('\t{0:<30} {1:>12.7f} sec'.format(key, float(val)))


# t = Benchmarking()
# from time import sleep
# t.toggle_timer('dsa')
# sleep(1)
# t.toggle_timer('dsa')
# sleep(0.5)
# t.toggle_timer('dsa')
# sleep(0.3)
# # t.toggle_timer('dsa')
#
# t.print_timers()
