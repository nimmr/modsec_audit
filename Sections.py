import re
from ModsecException import ModsecException
import bz2

__author__ = 'Tim Lund <code@nimmr.dk>'


class Sections:

    def __init__(self, sections):

        self.errors = dict()

        self.a = None
        self.b = None
        # self.f = None
        self.h = None
        # self.k = None

        self.compressed_audit_contents = None

        if 'A' in sections:
            try:
                self.a = A.create_from_string(sections['A'])
            except ModsecException, e:
                self.errors['A'] = e
        else:
            self.errors['A'] = ModsecException("Section A not present in audit log")

        if 'B' in sections:
            try:
                self.b = B.create_from_string(sections['B'])
            except ModsecException, e:
                self.errors['B'] = e
        else:
            self.errors['B'] = ModsecException("Section B not present in audit log")


        # try:
        #     self.f = F(sections['F'])
        # except ModsecException, e:
        #     self.errors.append('F')

        if 'H' in sections:
            try:
                self.h = H.create_from_string(sections['H'])
            except ModsecException, e:
                self.errors['H'] = e
        else:
            self.errors['H'] = ModsecException("Section H not present in audit log")

        # try:
        #     self.k = K(sections['K'])
        # except ModsecException, e:
        #     self.errors.append('K')


    def get_errors(self):
        """

        :return: list
        """
        return self.errors


    def __repr__(self):
        return "Section(a={0}, b={1}, h={2})".format(
            self.a, self.b, self.h
        )



class A:
    """

    """

    def __init__(self, uniq, remote_ip, server_ip):
        self.uniq = uniq
        self.remote_ip = remote_ip
        self.server_ip = server_ip


    @staticmethod
    def create_from_string(string):
        """
        :param string:
        :return: A
        """

        pattern = r"""
            # Used this for datetime.
            #\[ ([^\]]+) \] .*? (\d+\.\d+\.\d+\.\d+)

            \]\s ([^\s]+)\s

            (\d+\. \d+\. \d+\. \d+) .*? (\d+\. \d+\. \d+\. \d+)
        """

        reg = re.compile(pattern, re.S | re.I | re.X)
        matches = reg.search(string)

        if not matches:
            raise ModsecException(message='Could not match section A')

        return A(matches.group(1), matches.group(2), matches.group(3))


    def __repr__(self):
        return "A(uniq='{0} 'remote_id='{1}', server_ip='{2}')".format(
            self.uniq, self.remote_ip, self.server_ip
        )



class B:

    def __init__(self, host, url, site):
        self.host = host
        self.url = url
        self.site = site


    @staticmethod
    def create_from_string(string):
        """
        :param string:
        :return: B
        """

        pattern = r"""
            [GET|POST]\s ([^\s]+).*?
            Host:\s ([^\n]+).*?
        """

        reg = re.compile(pattern, re.S | re.I | re.X)
        matches = reg.search(string)

        if not matches:
            raise ModsecException('Could not parse section B')

        host = matches.group(2)

        return B(host, matches.group(1), '.'.join(host.split('.')[-2:]))


    def __repr__(self):
        return "B(host='{0}', url='{1}', site='{2}')".format(self.host, self.url, self.site)


# class F:
#
#     def __init__(self, string):
#         pass


class H:

    def __init__(self, id=0, message=''):
        self.message = message
        self.id = id
        self.modsec_error = None

    @staticmethod
    def create_from_string(string):
        """
        :param string:
        :return: H
        """

        pattern = r"""
            Message:\s* ([^\n]+).*?
        """

        reg = re.compile(pattern, re.S | re.I | re.X)
        matches = reg.search(string)

        if not matches:
            raise ModsecException('Could not parse section H')

        idpat = r"""
            id\s* "(\d+)"\]
            (?:.*?\])*
            \s*(.*)
        """

        reg = re.compile(idpat, re.S | re.I | re.X)
        idmatches = reg.search(matches.group(1))

        if not idmatches:
            raise ModsecException(matches.group(1))

        return H(idmatches.group(1), idmatches.group(2))


    def __repr__(self):
        return "H(message='{0}', id={1})".format(self.message, self.id)

#
# class K:
#
#     def __init__(self, string):
#         pass