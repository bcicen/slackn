import os
import logging
import sqlite3

class Slackn(object):
    def __init__(self, dbpath='/tmp/slackn.db'):
        self.conn = sqlite3.connect(dbpath)
        self.cursor = self.conn.cursor()
        if 'notifications' not in self._tables():
            self._initdb()

    def _initdb(self):
        query = ('''create table notifications
                    (host_alias text,
                     host_state text,
                     host_output text)''')
        self.cursor.execute(query)

    def _tables(self):
        """ Return a list of all table names """
        query = '''select name from sqlite_master where type = 'table''''
        return [ i[0] for i in self.cursor.execute(query).fetchall() ]
