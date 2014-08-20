from ModsecAudit import ModsecAudit
from settings import settings
import traceback
import sys

__author__ = 'tl'

ma = ModsecAudit(verbose=True, settings=settings)

try:
    ma.init_db()
    ma.main()
except KeyboardInterrupt, e:
    pass
except Exception, e:

    ma.print_color("An error occurred:", ma.COLOR_RED)
    ma.print_color("\t" + str(e.__class__), ma.COLOR_RED)
    ma.print_color("\t" + e.message, ma.COLOR_RED)

    traceback.print_tb(sys.exc_traceback)

finally:
    ma.end()

# def signal_handler(sig, frame):
#     print('closing down, caught signal: {0}'.format(sig))
#     sys.exit(1)
#
# signal.signal(signal.SIGINT, signal_handler)

