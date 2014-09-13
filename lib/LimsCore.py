import textwrap
import os
import inspect
import re
import xmltodict
import time
import pymysql
import hashlib
import string
import random
from pprintpp import pprint as pp
from http import cookies

class EmptyClass:
    pass

# Global NameSpace to convey data to the calling module
Data = EmptyClass()
Data.log = ''

# read in config xml and convert xml to an object
# ie.  config['LIMS']['software']['blast'] = path to local blast installation

with open('../config/config.xml.protected') as x:
    xml = x.read()
    config = xmltodict.parse(xml)


class LimsDB:
    def __init__(self, user_id, user_passwd, database_name):

        # connect to the database and define a cursor
        connection_credentials = {'user': user_id, 'passwd': user_passwd, 'host': 'localhost', 'port': 3306, 'db': database_name}

        try:
            self.conn = pymysql.connect(**connection_credentials)
            self.cur = self.conn.cursor(pymysql.cursors.DictCursor)
        except:
            error_msg = "Error.<br>Could not connect to the database '{0}' using user id '{1}' with password '{2}'".format(database_name, user_id, user_passwd)
            print(error_msg)
            exit()

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

    def privileges(self, required_privileges=''):
        gr = self.fetchall("show grants")
        gr.pop(0)

        tr = self.fetchall("show tables")
        tr.pop(0)

        all_actions = ['SELECT', 'UPDATE', 'INSERT', 'DELETE']

        privileges = {}

        Data.tr = tr

        for r in gr:
            for k in r:
                p = re.compile(r'^GRANT\s(?P<actions>.+?)\sON\s\`(?P<database>[^\`]+)\`\.\`?(?P<table>.+?)\`?\sTO')
                m = p.search(r[k])
                md = m.groupdict()

                if ( md ):

                    if md['table'] is '*':
                        for t in tr:
                            for table in t:
                                if md['table'] not in privileges:
                                    privileges[table] = {}

                                for action in ( re.split(r'\s*,?\s*', md['actions']) ):
                                    action.strip()

                                    if (action is '*'):
                                        for a in all_actions:
                                            privileges[table][a] = True
                                    else:
                                        privileges[table][action] = True
                    else:
                        if md['table'] not in privileges:
                            privileges[md['table']] = {}

                        for action in ( re.split(r'\s*,?\s*', md['actions']) ):
                            action.strip()

                            if (action is '*'):
                                for a in all_actions:
                                    privileges[md['table']][a] = True
                            else:
                                privileges[md['table']][action] = True
                else:
                    print("Error, can not parse MySQL privileges")
                    exit()

        return privileges

def start_cgi_page(page_title='untitled'):
    import cgitb
    import cgi

    cgitb.enable(display=1, logdir="tmp")

    # Make cgi.FieldStorage available to the calling script via the Data name space
    Data.cgi = cgi.FieldStorage()

    # Store variable, value pairs from cgi.FieldStorage in Data.cgiVars dict for easy access and manipulation
    Data.cgiVars = {}
    for v in Data.cgi:
        Data.cgiVars[v] = Data.cgi[v].value

    # parse cookies
    parsedCookies = {}
    cookiesToSet = cookies.SimpleCookie()

    if 'HTTP_COOKIE' in os.environ:
        cookie_list = os.environ['HTTP_COOKIE'].split(';')

        for cookie in cookie_list:
            cookie_var, cookie_value= cookie.split('=')
            parsedCookies[cookie_var.strip()] = cookie_value.strip()

    # Specific variables need to be stored in both Data.cgiVars and http cookies.
    # If a variable is found in Data.cgiVars but not stored as a cookie then set the cookie
    # If a variable is found in a cookie but not already stored in Data.cgiVars then store the variable in Data.cgiVars
    cookieVariables = ['user_id', 'user_passwd', 'database_name']
    for v in cookieVariables:
        if v in Data.cgiVars and v not in parsedCookies:
            cookiesToSet[v] = Data.cgiVars[v]
        elif v in parsedCookies and v not in Data.cgiVars:
            Data.cgiVars[v] = parsedCookies[v]
        else:
            pass

    # Determine the name of the script calling this module and determine if there is a coresponding
    # .js file.  ie.  protein.cgi call this module then check for protein.js
    # If the file exists then add a line to the header to import the js file and then print the HTML header.
    # Do the same for .css files then print the default LIMS header including the relevant js and css code.

    # determine the name of the script calling this module
    m = re.search(r'([^/]+)$', inspect.stack()[1][1], re.M | re.I)
    calling_file = m.group(1)

    js_file = re.sub(r'\.\w+$', '.js', inspect.stack()[1][1])
    m = re.search(r'([^/]+)$', js_file, re.M | re.I)
    js_file = 'js/' + m.group(1)
    js_code = ''

    if os.path.isfile(js_file):
        js_code += "<script type='text/javascript' src='{0}'></script>\n".format(js_file)
    if os.path.isfile('js/all.js'):
        js_code += "<script type='text/javascript' src='js/all.js'></script>\n"

    css_file = re.sub(r'\.\w+$', '.css', inspect.stack()[1][1])
    m = re.search(r'([^/]+)$', css_file, re.M | re.I)
    css_file = 'css/' + m.group(1)
    css_code = ''

    if os.path.isfile(css_file):
        css_code += "<link rel='stylesheet' type='text/css' href='{0}'>\n".format(css_file)
    if os.path.isfile('css/all.css'):
        css_code += "<link rel='stylesheet' type='text/css' href='css/all.css'>\n"


    # Assemble the HTML header
    html_header = """\
    {0}
    Content-type: text/html

    <html>
     <head>
      <title>{1}</title>
      {2}
      {3}
    </head>
    <body>
    <table style='width:100%; border-collapse: collapse;'>
     <tr>
      <td style='padding: 0px; width:50px'><img src='../img/icons/science2.png' style='height:35px'></td>
      <td style='padding: 0px; text-align: left;'>PyLIMS</td>
      <td style='padding: 0px; text-align: right;'><div id='login_info'></div></td>
     </tr>
    </table>
    """.format(cookiesToSet.output(), page_title, js_code, css_code)

    # Present the login screen if the user can not be identified from LIMS cookies or a login attempt   

    if 'user_id' not in Data.cgiVars:
        s = """\
        <br>
            <table style='border-collapse: collapse;'>
             <tr style='vertical-align:top'>
              <td style='padding: 0px; width:50px; text-align: left;'>
                <img src ='../img/icons/small57.png' style='height:30px'>
              </td>
              <td style='text-align: left;'>PyLIMS is restricted to registered users.<br>Please sign in.</td>
              <td style='width:10px'></td>
              <td style='padding: 0px; text-align: left;'>
                <form name="login" accept-charset="UTF-8" action="%s" method="post">
                  <table style='border-collapse: collapse;'>
                   <tr style='vertical-align:top'>
                    <td>user id</td>
                    <td style='width:10px'></td>
                    <td><input type='text' name='user_id'></td>
                   </tr>
                   <tr style='vertical-align:top'>
                    <td>password</td>
                    <td style='width:10px'></td>
                    <td><input type='text' name='user_passwd'></td>
                   </tr>
                   <tr style='vertical-align:top'>
                    <td>database</td>
                    <td style='width:10px'></td>
                    <td><input type='text' name='database_name'></td>
                   </tr>
                   <tr style='vertical-align:top'><td><input type='submit' value='log in'></td></tr>
                  </table>
                  <input type='hidden' name='action' value='verify_user_login'>
                </form>
              </td>
             </tr>
            </table>
        """ % calling_file

        print(textwrap.dedent(html_header).strip())
        print(textwrap.dedent(s))
        end_cgi_page()
        exit()
    else:
        # User successfully logged in via cookie
        print(textwrap.dedent(html_header).strip())

        # Update interface header with login info
        print("<script>document.getElementById('login_info').innerHTML='{0}'</script>\n".format(Data.cgiVars['user_id']))

    return

def end_cgi_page(id_length=5):
    print('</body></html>')
    return 0

def create_randomized_id(length=5, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(length))

def create_sequence_digest(sequence):
    hash = hashlib.sha1()
    hash.update(sequence.encode('utf-8'))
    return hash.hexdigest()