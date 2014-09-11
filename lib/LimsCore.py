import textwrap
import os
import inspect
import re
import xmltodict
import time
import pymysql
import hashlib
from http import cookies

# done 123

class EmptyClass:
    pass

# Global NameSpace to convey data to the calling module
Data = EmptyClass()

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
        qr = self.fetchall("show grants")
        qr.pop(0)

        privileges = {}

        for r in qr:
            for k in r:
                p = re.compile(r'^GRANT\s(?P<actions>.+?)\sON\s\`(?P<database>[^\`]+)\`\.\`?(?P<table>.+?)\`?\sTO')
                m = p.search(r[k])
                md = m.groupdict()

                if ( md ):

                    if md['table'] is '*':
                        md['table'] = 'ALL TABLES'

                    for action in ( re.split(r'\s*,?\s*', md['actions']) ):
                        action.strip()
                        if ( action is '*'):
                            action = 'ALL ACTIONS'

                        if md['table'] not in privileges:
                            privileges[md['table']] = {}
                            privileges[md['table']][action] = True

                        else:
                            if action not in privileges[md['table']]:
                                privileges[md['table']][action] = True
                else:
                    print("Error, can not parse MySQL privileges")
                    exit()

        return privileges

def start_cgi_page(page_title='untitled'):
    import cgitb
    import cgi

    cgitb.enable(display=1, logdir="tmp")

    Data.cgi = cgi.FieldStorage()
    Data.log = "start<br>"

    for v in Data.cgi:
        Data.log += "Data.cgi |{0}| |{1}|<br>".format(v, Data.cgi[v].value)

    # parse cookies
    parsedCookies = {}
    cookiesToSet = cookies.SimpleCookie()


    if 'HTTP_COOKIE' in os.environ:
        cookie_list = os.environ['HTTP_COOKIE'].split(';')

        Data.log += "Cookie parser ({0})<br>".format(os.environ['HTTP_COOKIE'])

        for cookie in cookie_list:
            cookie_var, cookie_value= cookie.split('=')
            parsedCookies[cookie_var.strip()] = cookie_value.strip()

    cookieVariables = ['user_id', 'user_passwd', 'database_name', 'test']
    for v in cookieVariables:
        if v in Data.cgi and v not in parsedCookies:
            cookiesToSet[v] = Data.cgi[v].value
            Data.log += "+ requesting cookie |{0}| |{1}|<br>".format(v, Data.cgi[v].value)
        elif v in parsedCookies and v not in Data.cgi:
            Data.cgi.add_field(v, parsedCookies[v])
            #Data.cgi[v] = parsedCookies[v]
            Data.log += "~ adding cookie data to Data.cgi |{0}| |{1}|<br>".format(v, parsedCookies[v])
    else:
        pass

    cookiesToSet['test'] = 'test_value'


    # determine the name of the script calling this module
    m = re.search(r'([^/]+)$', inspect.stack()[1][1], re.M | re.I)
    calling_file = m.group(1)

    # Determine the name of the script calling this module and determine if there is a coresponding
    # .js file.  ie.  protein.cgi call this modeule then check for protein.js
    # If the file exists then add a line to the header to import the js file and then prtin the HTML header.
    # Do the same for .css files then print the default LIMS header including the relevant js and css code.

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

    html_header = '''{0}
    Content-type: text/html

    <html>
     <head>
      <title>{1}</title>
      {2}
      {3}
    </head>
    <body>	
    <table style='border-collapse: collapse;'><tr>
     <td style='padding: 0px'><img src='../img/icons/science2.png' style='height:40px'> &nbsp; </td>
     <td style='padding: 0px'>&nbsp; LIMS  ({4})</td></tr></table>
    '''.format(cookiesToSet.output(), page_title, js_code, css_code, 'user_id')

    # Present the login screen if the user can not be identified from LIMS cookies or a login attempt   

    if 'user_id' not in Data.cgi:
        s = '''<br>
            <table><tr style='vertical-align:top'><td><img src ='../img/icons/small57.png' style='height:30px'></td>
                   <td style='width:15px'></td>
                   <td>LIMS is restricted to registered users.<br>Please sign in.</td><td style='width:15px'></td>
                       <td>
                          <form name=login action='%s' method='post'>
                             <table>
                               <tr style='vertical-align:top'>
                                 <td>user id</td>
                                 <td><input type='text' name='user_id'></td>
                                </tr>
                               <tr style='vertical-align:top'>
                                <td>password</td>
                                <td><input type='text' name='user_passwd'></td>
                               </tr>
                               <tr style='vertical-align:top'>
                                <td>database</td>
                                <td><input type='text' name='database_name'></td>
                               </tr>
                               <tr style='vertical-align:top'><td><input type='submit'></td></tr>
                             </table>
                             <input type='hidden' name='action' value='verify_user_login'>
                           </form>
                       </td></tr></table>
        ''' % calling_file

        print(textwrap.dedent(html_header))
        print(textwrap.dedent(s))
        end_cgi_page()
        exit()
    else:
        # User successfully logged in via cookie
        print(textwrap.dedent(html_header))

        print("Cookie object: ", cookiesToSet, "<br><br>")

    return

def end_cgi_page():
    print('</body></html>')
    return 0