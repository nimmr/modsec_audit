from sqlalchemy.sql.sqltypes import LargeBinary

__author__ = 'tl'

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.orm import relationship, backref
from sqlalchemy import ForeignKey
from datetime import datetime
import Benchmarking
import ModsecAudit

Base = declarative_base()

class ModsecDb:

    def __init__(self, modsec):
        """
        :param modsec: ModsecAudit
        """


        self.modsec = modsec
        """:type: ModsecAudit.ModsecAudit"""
        self.settings = modsec.settings['db']
        self.engine = create_engine(self.settings['connection_string'])
        self.run_status = None
        """:type: RunStatus"""

        self.site_cache = dict()
        self.ip_cache = dict()
        self.timers = modsec.timers
        """:type: Benchmarking.Benchmarking"""

        sm = sessionmaker(bind=self.engine)
        self.session = sm()
        """:type: Session"""


    def get_session(self):
        """
        :return: Session
        """
        return self.session


    def get_engine(self):
        return self.engine


    def mark_status(self, status, parsed=None, parse_errors=None):
        """
        Defines the start in runstatus
        """
        if self.run_status is None:
            self.run_status = RunStatus(run_date=datetime.now(), status=status)
            self._add_and_commit(self.run_status)
        else:
            self.run_status.status = status

            if parsed:
                self.run_status.parsed = parsed
            if parse_errors:
                self.run_status.parse_errors = parse_errors

            self.session.commit()


    def create_site(self, name):
        """

        :param name: string
        :return: Site
        """
        if name in self.site_cache:
            return self.site_cache[name]

        site = self.get_site(name)

        if site:
            return site

        self.timers.toggle_timer('db.create_site.new_site')
        self.modsec.counter('db.create_site.new_site')

        now = datetime.now()

        site = Site(
            site=name,
            added=now,
            last_run_date=now,
            total_count=0
        )

        # self._add_and_commit(site)
        self.session.add(site)
        self.timers.toggle_timer('db.create_site.new_site')

        return site


    def get_site(self, name):
        """
        :param name: string
        :return: Site
        """
        return self.get_session().query(Site).filter_by(site=name).first()


    def create_ip(self, ip):
        """

        :param ip: string
        :return: Ip
        """
        if ip in self.ip_cache:
            return self.ip_cache[ip]

        new_ip = self.get_ip(ip)

        if new_ip:
            return new_ip

        self.timers.toggle_timer('db.create_ip.new_ip')
        self.modsec.counter('db.create_ip.new_ip')

        new_ip = Ip(
            ip=ip
        )

        self._add_and_commit(new_ip)
        # self.session.add(new_ip)
        self.timers.toggle_timer('db.create_ip.new_ip')

        return new_ip

    def get_ip(self, ip):
        """
        :param ip: string
        :return: Ip
        """
        return self.get_session().query(Ip).filter_by(ip=ip).first()


    def create_hit(self, uniq, site, ip, at, modsec_id, contents):
        """
        :param uniq: string
        :param site_id: int
        :param ip_id: int
        :param at: datetime
        :param modsec_id: int
        :param contents: str
        :return: Hit
        """

        self.timers.toggle_timer('db.create_hit.new_hit')
        self.modsec.counter('db.create_hit.new_hit')

        hit = Hit(
            uniq=uniq,
            site_id=site.id,
            ip_id=ip.id,
            datetime = at,
            modsec_id=modsec_id,
            contents=contents
        )


        self.session.add(hit)
        # self._add_and_commit(hit)
        self.timers.toggle_timer('db.create_hit.new_hit')

        return hit


    def create_parse_error(self, runstatus_id, file, message, contents):
        """
        :param runstatus_id: int
        :param file: str
        :param message: str
        :param message: str
        :return: ParseError
        """

        pe = ParseError(runstatus_id=runstatus_id, file=file, message=message, contents=contents)
        self.session.add(pe)

        return pe


    def _add_and_commit(self, obj):
        """
        Commits the obj to the db immediately
        """
        self.session.add(obj)
        self.session.commit()
        self.session.flush()


    def delete_all(self):
        """
        only for dev
        """
        self.session.execute("delete from {}".format(Hit.__tablename__))
        self.session.execute("delete from {}".format(Ip.__tablename__))
        self.session.execute("delete from {}".format(Site.__tablename__))
        self.session.execute("delete from {}".format(RunStatus.__tablename__))
        self.session.execute("delete from {}".format(ParseError.__tablename__))
        self.session.commit()
        self.session.flush()

    def test(self):

        ses = self.get_session()
        # s = Site(site='tv2.dk', added='2014-05-13 20:54:01', last_run_date='2014-05-13 20:54:01', total_count=2)
        # ses.add(s)
        # ses.commit()

        # f = self.session.query(Site).filter_by(site='tv2.dk').first()
        # print f
        # print ses.new

        hit = self.session.query(Hit).filter_by(site_id=9).first()
        print hit

        print hit.site




class Site(Base):

    __tablename__ = 'modsec_site'

    id = Column(Integer, primary_key=True)
    site = Column(String)
    added = Column(DateTime)
    last_run_date = Column(DateTime)
    last_parsed_date = Column(DateTime)
    total_count = Column(Integer)

    def __repr__(self):
        return (
            "<Site (id={}, site={}, added={}, lastRunDate={}, lastParsedDate={}, totalCount={})>".format(
                self.id, self.site, self.added, self.last_run_date, self.last_parsed_date, self.total_count
            )
        )

class Ip(Base):

    __tablename__ = 'modsec_ip'

    id = Column(Integer, primary_key=True)
    ip = Column(String)

    def __repr__(self):
        return "<Ip (id={}, ip={})>".format(self.id, self.ip)


class RunStatus(Base):

    __tablename__ = 'modsec_runstatus'

    id          = Column(Integer, primary_key=True)
    run_date    = Column(DateTime)
    status      = Column(String)
    parsed      = Column(Integer)
    parse_errors= Column(Integer)

    def __repr__(self):
        return "<RunStatus (id={}, run_date={}, status={}, parsed={}, parse_errors={})>".format(
            self.id, self.run_date, self.status, self.parsed, self.parse_errors
        )

class Hit(Base):

    __tablename__ = 'modsec_hit'

    uniq = Column(String, primary_key=True)
    site_id = Column(Integer, ForeignKey('modsec_site.id'))
    ip_id = Column(Integer, ForeignKey('modsec_ip.id'))
    datetime = Column(DateTime)
    modsec_id = Column(Integer)
    contents = Column(LargeBinary)

    site = relationship('Site', backref=backref('modsec_hit', order_by=datetime))

    def __repr__(self):
        return (
            "<Hit (uniq={}, site_id={}, ip_id={}, datetime={}, modsec_id={})>".format(
                self.uniq, self.site_id, self.ip_id, self.datetime, self.modsec_id
            )
        )

class ParseError(Base):

    __tablename__ = 'modsec_parse_error'

    id              = Column(Integer, primary_key=True)
    runstatus_id    = Column(Integer, ForeignKey('modsec_runstatus.id'))
    file            = Column(String)
    message         = Column(String)
    contents        = Column(LargeBinary)

    runstatus = relationship('RunStatus', backref=backref('modsec_parse_error'))

    def __repr__(self):
        return (
            "ParseError(id={}, runstatus_id={}, file='{}', message='{}')".format(
                self.id, self.runstatus_id, self.file, self.message
            )
        )


# db = ModsecDb({'connection_string' : 'mysql://root@127.0.0.1/system'})
# db.test()
