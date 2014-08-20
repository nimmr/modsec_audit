import os
from unittest import TestCase
from ModsecAudit import ModsecAudit
from ModsecException import ModsecException
from ModsecDb import Hit, Ip, RunStatus, Site, ParseError
from settings import settings
import shutil

__author__ = 'tl'


class TestModsecAudit(TestCase):

    def test_settings_missing(self):

        with self.assertRaises(ModsecException) as ctx:
            ms = ModsecAudit()

        self.assertEqual(ModsecException.ERR_CFG_MISSING, ctx.exception.get_code())

    def test_settings_incomplete(self):

        with self.assertRaises(ModsecException) as ctx:
            ms = ModsecAudit(settings={ 'blah' : 1 })

        self.assertEqual(ModsecException.ERR_CFG_INCOMPLETE, ctx.exception.get_code())


    def test_no_spaces_on_folder(self):

        s = {
            'folders'       : {
                'auditLogs'     : '/var /log/modsec/',
                'archive'       : os.path.dirname(__file__),
                'workRoot'      : os.path.dirname(__file__),
            }
        }

        with self.assertRaises(ModsecException) as ctx:
            ms = ModsecAudit(settings=s)

        self.assertEqual(ModsecException.ERR_CFG_NO_SPACES_IN_FOLDER, ctx.exception.get_code())


    def test_folder_cannot_be_slash(self):

        s= {
            'folders'       : {
                'auditLogs'     : '/',
                'archive'       : os.path.dirname(__file__),
                'workRoot'      : os.path.dirname(__file__),
            }
        }

        with self.assertRaises(ModsecException) as ctx:
            ms = ModsecAudit(settings=s)

        self.assertEqual(ModsecException.ERR_CFG_FOLDER_NOT_ROOT, ctx.exception.get_code())


    def test_folder_cannot_be_root_win_drive(self):

        s= {
            'folders'       : {
                'auditLogs'     : 'd:\\',
                'archive'       : os.path.dirname(__file__),
                'workRoot'      : os.path.dirname(__file__),
            }
        }

        with self.assertRaises(ModsecException) as ctx:
            ms = ModsecAudit(settings=s)

        self.assertEqual(ModsecException.ERR_CFG_FOLDER_NOT_ROOT, ctx.exception.get_code())


    def test_verify_test_run(self):
        """
        Bad example of a unit test. This method verifies that with the test data
        everything is registered correctly in the db.

        :return:
        """

        self.remove_archive_folders()

        ma = ModsecAudit(verbose=True, settings=settings)
        ma.set_exit_on_end(False)
        ma.init_db()

        self.empty_tables(ma)

        ma.main()
        ma.end()

        self.check_runstatus(ma)
        self.check_sites(ma)
        self.check_ips(ma)
        self.check_hits(ma)
        self.check_parse_errors(ma)



    def check_runstatus(self, ma):
        """
        :param ma: ModsecAudit
        :return:
        """

        session = ma.db.get_session()

        rs = session.query(RunStatus).all()

        self.assertEqual(1, len(rs))
        self.assertEqual('done', rs[0].status)
        self.assertEqual(10, rs[0].parsed)
        self.assertEqual(3, rs[0].parse_errors)


    def check_sites(self, ma):
        """
        :param ma: ModsecAudit
        :return:
        """

        session = ma.db.get_session()

        required = ('url12.tld', 'url2.tld', 'url4.tld', 'url5.tld', 'url7.tld', 'url9.tld')
        count = session.query(Site).filter(Site.site.in_(required)).count()
        self.assertEqual(6, count)


    def check_ips(self, ma):
        """
        :param ma: ModsecAudit
        :return:
        """

        session = ma.db.get_session()

        required = ('192.168.1.2', '192.168.1.3', '192.168.2.1', '192.168.3.1', '192.168.9.1', '192.168.11.1')
        count = session.query(Ip).filter(Ip.ip.in_(required)).count()
        self.assertEqual(6, count)


    def check_hits(self, ma):
        """
        :param ma: ModsecAudit
        :return:
        """

        session = ma.db.get_session()

        # uniq's

        required = (
            'M2JVn1Eb3loAAF0jYaMAAAAB','0GJ7CFEb3loAAHsWZNgAAAAJ','zBWA1lEb3loAAHiffdwAAAAd',
            'dbT8zFEb3loAAEGp9DYAAAAJ','71E6u1Eb3loAAEOzFVcAAAAr','cHhVAlEb3loAAGBlpBoAAAAc',
            'Rzald1Eb3loAAGMIN5sAAAAb','R06EelEb3loAAGr1rPgAAAAw','WykqXFEb3loAAFtmZIYAAAAS',
            'HsH04lEb3loAAEoCCXUAAAAk'
        )

        count = session.query(Hit).filter(Hit.uniq.in_(required)).count()
        self.assertEqual(10, count)

        # dates

        required = (
            '2012-09-21 14:15:51', '2013-08-27 14:14:26', '2013-01-30 18:25:32',
            '2013-08-27 06:39:35', '2014-01-13 00:01:09', '2013-08-27 13:47:37',
            '2014-01-14 01:28:58', '2014-01-14 01:28:59', '2014-01-15 01:26:43',
            '2014-01-15 16:39:53'
        )

        count = session.query(Hit).filter(Hit.datetime.in_(required)).count()
        self.assertEqual(10, count)

        # modsec_id's

        counts = session.execute(
            "select modsec_id, count(*) as cnt from {} group by modsec_id".format(Hit.__tablename__)
        )

        d = {}
        for r in counts:
            d[r[0]] = r[1]

        self.assertEqual(1, d[2000])
        self.assertEqual(6, d[2002])
        self.assertEqual(2, d[2011])
        self.assertEqual(1, d[2050])





    def check_parse_errors(self, ma):
        """
        :param ma: ModsecAudit
        :return:
        """

        session = ma.db.get_session()

        count = session.query(ParseError).count()
        self.assertEqual(3, count)


    #
    #       Helper methods
    #




    def empty_tables(self, ma):
        """
        :param ma: ModsecAudit
        :return:
        """
        session = ma.db.get_session()

        ma.db.delete_all()

        self.assertEqual(0, session.query(Site.id).count(), "Table site not empty")
        self.assertEqual(0, session.query(Ip.id).count(), "Table ip not empty")
        self.assertEqual(0, session.query(Hit.uniq).count(), "Table hit not empty")
        self.assertEqual(0, session.query(RunStatus.id).count(), "Table runstatus not empty")
        self.assertEqual(0, session.query(ParseError.id).count(), "Table parse_error not empty")



    def remove_archive_folders(self):

        # for d in [x[0] for x in os.walk( settings['folders']['archive'] )]:
        for d in [x for x in os.listdir( settings['folders']['archive'] )]:
            path = os.path.join(settings['folders']['archive'],d)
            os.remove(path)
            # Old dir style
            # ModsecAudit.check_folder('test', path)
            # shutil.rmtree(path)