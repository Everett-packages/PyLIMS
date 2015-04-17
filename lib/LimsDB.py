import pymysql
import re


class DB:
    """ The DB class connects to a MySQL database with the provided credentials, provides a number
        of methods for interacting with the database and provides additional methods to determine a users
        level of access to the database. """

    def __init__(self, user_id, user_passwd, database_name):

        # connect to the database and define a cursor
        connection_credentials = {'user': user_id, 'passwd': user_passwd, 'host': 'localhost', 'port': 3306,
                                  'db': database_name, 'autocommit': True}
        try:
            self.conn = pymysql.connect(**connection_credentials)
            self.cur = self.conn.cursor(pymysql.cursors.DictCursor)
        except:
            error_msg = "Error.<br>Could not connect to the database '{0}' using user id '{1}' with password '{2}'". \
                format(database_name, user_id, user_passwd)
            print(error_msg)
            exit()

    def execute(self, query):
        try:
            self.cur.execute(query)

        except self.cur.Error as e:
            try:
                print("MySQL Error [%d]: %s" % (e.args[0], e.args[1]))
            except IndexError:
                print("MySQL Error: %s" % str(e))
        exit()
        return

    def fetchvalue(self, query):
        self.cur.execute(query)
        row = self.cur.fetchone()
        return row[row.keys()[0]]

    def fetchone(self, query):
        self.cur.execute(query)
        row = self.cur.fetchone()
        return row

    def fetchall(self, query):
        self.cur.execute(query)
        rows = self.cur.fetchall()
        r = []
        for row in rows:
            r.append(row)
        return r

    def disconnect(self):
        self.cur.close()
        self.conn.close()

    def privileges(self):
        """ This method determines which tables the current user can access and the extent of that access.
            and returns a dict of dicts detailing the users access level, ie. { construct table: { insert: True} }.
            Developers should create and consult this data object before attempting to work with the database.
        """
        gr = self.fetchall("show grants")
        gr.pop(0)

        tr = self.fetchall("show tables")

        tables = []
        for t in tr:
            for tt in t:
                tables.append(t[tt])

        # List to translate '*' to select actions.  Certain actions such as DROP are currently not supported.
        all_actions = ['SELECT', 'UPDATE', 'INSERT', 'DELETE']

        privileges = {}

        for r in gr:
            for k in r:
                p = re.compile(r'^GRANT\s(?P<actions>.+?)\sON\s`(?P<database>[^`]+)`.`?(?P<table>.+?)`?\sTO')
                m = p.search(r[k])
                md = m.groupdict()

                if md['actions'] == "ALL PRIVILEGES":
                    md['actions'] = ', '.join(all_actions)

                if md:
                    if md['table'] is '*':
                        for table in tables:
                            if table not in privileges:
                                privileges[table] = {}

                            for action in (re.split(r'\s*,?\s*', md['actions'])):
                                action.strip()

                                if action is '*':
                                    for a in all_actions:
                                        privileges[table][a] = True
                                else:
                                    privileges[table][action] = True

                    else:
                        if md['table'] not in privileges:
                            privileges[md['table']] = {}

                        for action in (re.split(r'\s*,?\s*', md['actions'])):
                            action.strip()

                            if action is '*':
                                for a in all_actions:
                                    privileges[md['table']][a] = True
                            else:
                                privileges[md['table']][action] = True
                else:
                    print("Error, can not parse MySQL privileges")
                    exit()

        return privileges