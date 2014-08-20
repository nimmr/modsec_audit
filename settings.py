import os

#
# This settings file is for unit tests.
#

__author__ = 'tl'

settings = {

    'folders' : {
        # 'errorLogs'             :'/var/log/apache/',
        'auditLogs'     : os.path.join(os.path.dirname(__file__), 'test', 'auditlogs'),
        'archive'       : os.path.join(os.path.dirname(__file__), 'test', 'archive'),
        'workRoot'      : os.path.join(os.path.dirname(__file__), 'test', 'workdir'),
    },


    'mkdir.mode' : 0750, # only when applicable

    'db'                        : {
        'connection_string'     : 'mysql://root@127.0.0.1/system',
    }
}