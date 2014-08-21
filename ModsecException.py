__author__ = 'Tim Lund <code@nimmr.dk>'


class ModsecException(Exception):

    #
    # Constants


    ERR_CFG_INCOMPLETE = 200
    ERR_CFG_NO_SPACES_IN_FOLDER = 201
    ERR_CFG_FOLDER_NOT_ROOT = 202
    ERR_CFG_NOT_A_FOLDER = 203
    ERR_CFG_MISSING = 204


    ERR_PARSING_AUDIT_LOG = 310


    #
    # attributes

    ER = {
        ERR_CFG_MISSING                 : "Cannot find settings.py",
        ERR_CFG_INCOMPLETE              : "Settings for this program is incomplete. Missing key: '{0}'",
        ERR_CFG_NO_SPACES_IN_FOLDER     : "There is a space in the folder '{0}': value '{1}'",
        ERR_CFG_FOLDER_NOT_ROOT         : "Config folder '{0}' cannot be '/'",
        ERR_CFG_NOT_A_FOLDER            : "Config folder '{0}' is not a folder: '{0}'",

        ERR_PARSING_AUDIT_LOG           : "Could not parse section(s): '{0}' in audit log: '{1}'",
    }

    code = 0

    #
    #
    #
    def __init__(self, message=None, code=None, *error_params):

        self.message = ''

        if code:
            self.code = code
            message = self.ER[code].format(*error_params)
        elif message:
            message = message
        else:
            pass # throw another exception? :p

        super(ModsecException, self).__init__(message)

    #
    #
    #
    def get_code(self):
        return self.code


    def get_message(self):
        """

        :return:
        """
        return self.message


