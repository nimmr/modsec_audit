from __future__ import print_function
from datetime import datetime, date
from CliScript import CliScript
from ModsecException import ModsecException
from Sections import Sections, A, B, H
import ModsecDb
import os
import shutil
import tarfile
import bz2
from sys import stderr

__author__ = 'Tim Lund <code@nimmr.dk>'

class ModsecAudit(CliScript):

    def __init__(self, settings={}, verbose=False):
        """
        init
        """

        self.settings = settings
        self.db = None
        """ :type: ModsecDb.ModsecDb"""
        self.errors = {}
        self._modsec_gracefully_ended = None
        self.top_folders = []

        self.check_settings(settings)

        self.workRoot = os.path.join(self.settings['folders']['workRoot'])

        super(ModsecAudit, self).__init__(verbose)


    def check_settings(self, settings):
        """
        not quite complete tests, but check if we have a CFG
        """

        if not settings or settings is {}:
            raise ModsecException('', ModsecException.ERR_CFG_MISSING)

        if not 'folders' in settings:
            raise ModsecException('', ModsecException.ERR_CFG_INCOMPLETE, 'folders')

        for key, folder in settings['folders'].items():
            self.check_folder(key, folder)


    @staticmethod
    def check_folder(key, folder):
        """
        We cant allow some folders in our setup, since later, we need to delete
        from these folders. That wouldn't be pleasant on ' ' or '/'
        """

        # @todo implement gzipping and deletion of dirs

        if ' ' in folder:
            raise ModsecException('', ModsecException.ERR_CFG_NO_SPACES_IN_FOLDER, key, folder)

        # wintendo folders
        if '\\' in folder:
            if len(folder) == 3:
                raise ModsecException('', ModsecException.ERR_CFG_FOLDER_NOT_ROOT, key)
        else:
            if len(folder) == 1 and folder == '/':
                raise ModsecException('', ModsecException.ERR_CFG_FOLDER_NOT_ROOT, key)

        if not os.path.isdir(folder):
            raise ModsecException('', ModsecException.ERR_CFG_NOT_A_FOLDER, key, folder)


    def end(self):
        """
        Shutdown and close cli script
        """

        if self._modsec_gracefully_ended is True:
            return None

        self.db.mark_status(
            'done',
            self.get_counter('main.parsed'),
            self.get_counter('main.parse_errors')
        )

        if len(self.errors) > 0:
            self.print_color("Errors encountered!", self.COLOR_RED)
            for errlvl, errors in self.errors.items():
                for error in errors:
                    stderr.write(error + "\n")

        self._modsec_gracefully_ended = True

        super(ModsecAudit, self).end()


    def log(self, level, msg):
        """
        Temporary logging method.
        :param level:
        :param msg:
        :return:
        """
        # @todo change to file based or stderr based logging

        if not level in self.errors:
            self.errors[level] = list()

        self.errors[level].append(msg)


    def init_db(self):

        self.timers.toggle_timer('main.db.connect')
        self.db = ModsecDb.ModsecDb(self)
        self.timers.toggle_timer('main.db.connect')


    def main(self):
        """
        Run program method
        """

        if self._verbose:
            self.print_color("Starting program", self.COLOR_BLUE)

        self.db.mark_status('started')


        # self.workRoot = os.path.join(self.settings['folders']['archive'], str(self.db.run_status.id))
        # os.mkdir(self.workRoot)

        self.timers.toggle_timer('main')

        lastdirs = []

        #
        # Audit log dir traversal

        for root, dir, files in os.walk(self.settings['folders']['auditLogs']):

            d = os.path.basename(root)

            if len(files) < 1:
                self.top_folders.append(d)
                continue


            if os.path.basename(self.settings['folders']['auditLogs']) == d:
                continue


            #
            # Find previous months in workdir

            yearmonth = d[0:4] + d[4:6]

            if not yearmonth in lastdirs:
                lastdirs.append(yearmonth)

            if  len(lastdirs) > 1:
                self.archive(lastdirs[0])
                lastdirs = lastdirs[1:]

            #
            # Make workdir

            self.timers.toggle_timer('main.create_dirs')

            # Create outer date and inner date/date-hourminute folder

            outer = d.split('-')[0]
            path = os.path.join(self.workRoot, outer)
            inner_path = os.path.join(self.workRoot, outer, d)

            if not os.path.exists(path):
                os.mkdir(path, self.settings['mkdir.mode'])

            if not os.path.exists(inner_path):
                os.mkdir(inner_path, self.settings['mkdir.mode'])

            self.timers.toggle_timer('main.create_dirs')

            #
            # Parse files

            for filename in files:

                # We need the date from the filename instead of the timestamp
                # registered inside the audit log. the timestamp can be off by
                # seconds, and then it would be impossible to match archive
                # files later.

                odate = datetime(
                    int(filename[0:4]), int(filename[4:6]), int(filename[6:8]),
                    int(filename[9:11]), int(filename[11:13]), int(filename[13:15])
                )

                filename = os.path.join(root, filename)

                sections = self.parse_audit_log(filename)
                self.counter('main.audit_logs')

                if sections is None:
                    # @todo this is bad and file needs to be logged
                    self.counter('main.parse_errors')
                else:
                    self.counter('main.parsed')
                    # print(sections)
                    self.process_sections(odate, sections)

                # @todo change to move
                shutil.copy2(filename, os.path.join(inner_path, os.path.basename(filename)))


        self.timers.toggle_timer('main')
        self.end()


    def archive(self, yearmonth):
        """
        Move folders in auditLogs dir to archive and compress them.

        :param yearmonth:
        :return:
        """

        outer = os.path.join(self.settings['folders']['archive'], yearmonth)
        # os.mkdir(outer, self.settings['mkdir.mode'])

        for d in self.top_folders:
            if d[0:6] != yearmonth:
                continue

            src = os.path.join(self.workRoot, d)
            tar = tarfile.open(os.path.join(outer) + '.tgz', 'w:gz')
            tar.add(src, arcname=os.path.basename(src))
            tar.close()


            # @todo change to move
            #shutil.copytree(
            #    os.path.join(self.workRoot, d),
            #    os.path.join(outer, d)
            #)

        return


    def parse_audit_log(self, filename):
        """
        Parses the audit file and stores to db.
        :return Sections
        """

        linecnt = 0
        section_chksum = None
        section = None
        sections = dict()
        contents = ''

        self.timers.toggle_timer('parse_audit_log.open_and_read')
        for line in open(filename):

            contents += line

            if linecnt == 0:
                section_chksum = line[2:10]

            linecnt += 1

            if len(line) > 10 and line[2:10] == section_chksum:
                section = line[11:12]
                continue

            if section not in sections:
                sections[section] = str()

            sections[section] += line

        self.timers.toggle_timer('parse_audit_log.open_and_read')

        self.timers.toggle_timer('sections.parse')
        parsed_sections = Sections(sections)
        self.timers.toggle_timer('sections.parse')

        self.timers.toggle_timer('sections.compress')
        parsed_sections.compressed_audit_contents = bz2.compress(contents)
        self.timers.toggle_timer('sections.compress')

        errors = parsed_sections.get_errors()
        errlen = len(errors)

        if errlen > 0:

            self.counter('parse_audit_log.section_errors', errlen)

            inner_msg = ''
            for key in errors:
                inner_msg += "\tSection {0}: {1}\n".format(key, errors[key].get_message())

            self.log(
                self.LOG_WARN,
                "Could not match section(s) '{0}' in auditlog: '{1}'.\nError(s):\n{2}".format(
                    ', '.join(errors.keys()),
                    filename,
                    inner_msg
                )
            )

            self.db.create_parse_error(
                runstatus_id=self.db.run_status.id,
                file= "/".join(filename.split('/')[-3:]),
                message=inner_msg,
                contents=parsed_sections.compressed_audit_contents
            )

            return None

        return parsed_sections


    def process_sections(self, at, sections):
        """

        :param at: datetime
        :param sections: Sections
        """

        self.timers.toggle_timer('process_sections')

        if sections.h.id == 2050 and sections.b.url == '/blocked.html':
            self.counter('process_sections.2050.skipped')

        site = self.db.create_site(sections.b.site)
        ip = self.db.create_ip(sections.a.remote_ip)

        hit = self.db.create_hit(
            sections.a.uniq,
            site,
            ip,
            at,
            sections.h.id,
            sections.compressed_audit_contents
        )

        self.timers.toggle_timer('process_sections')







