import textwrap
import os
import sys
import inspect
import re
import xmltodict
from time import gmtime, strftime
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

# read in config xml and convert xml to an object
# ie.  config['LIMS']['software']['blast'] = path to local blast installation

with open('../../config/config.xml.protected') as x:
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

    def privileges(self):
        gr = self.fetchall("show grants")
        gr.pop(0)

        tr = self.fetchall("show tables")

        tables = []
        for t in tr:
            for tt in t:
                tables.append(t[tt])

        all_actions = ['SELECT', 'UPDATE', 'INSERT', 'DELETE']

        privileges = {}

        for r in gr:
            for k in r:
                p = re.compile(r'^GRANT\s(?P<actions>.+?)\sON\s\`(?P<database>[^\`]+)\`\.\`?(?P<table>.+?)\`?\sTO')
                m = p.search(r[k])
                md = m.groupdict()

                if ( md ):

                    if md['table'] is '*':
                        for table in tables:
                            if table not in privileges:
                                privileges[table] = {}

                            for action in ( re.split(r'\s*,?\s*', md['actions']) ):
                                action.strip()

                                if action is '*':
                                    for a in all_actions:
                                         privileges[table][a] = True
                                else:
                                    privileges[table][action] = True

                    else:
                        if md['table'] not in privileges:
                            privileges[md['table']] = {}

                        for action in ( re.split(r'\s*,?\s*', md['actions']) ):
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

    def __lt__(self, *args, **kwargs):
        return super().__lt__(*args, **kwargs)


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
            parsedCookies[cookie_var.strip()] = cookie_value.replace('"', '').strip()

    # CGI log
    # Each user will have a log file used primarily for debugging purposes.
    # The name of the log file will be tracked with cookies and a new log file name
    # will be created if an existing log file name is not found in the user's cookies.

    Data.cgiVars['cgi_log_file'] = ''
    if 'cgi_log_file' in parsedCookies:
        Data.cgiVars['cgi_log_file'] = parsedCookies['cgi_log_file']
    else:
        Data.cgiVars['cgi_log_file'] = "../../logs/cgi/" + create_randomized_id(5) + ".log.html"

    # Start the log for this CGI page

    update_cgi_log('page_start', "starting page")

    # Specific variables need to be stored in both Data.cgiVars and http cookies.
    # If a variable is found in Data.cgiVars but not stored as a cookie then set the cookie
    # If a variable is found in a cookie but not already stored in Data.cgiVars then store the variable in Data.cgiVars

    cookieVariables = ['user_id', 'user_passwd', 'database_name', 'cgi_log_file']
    for v in cookieVariables:
        if v in Data.cgiVars and v not in parsedCookies:
            cookiesToSet[v] = Data.cgiVars[v]
            cookiesToSet[v]["path"] = "/"
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
    html_header = '''\
    {0}
    Content-type: text/html

    <html>
     <head>
     <meta content="text/html;charset=utf-8" http-equiv="Content-Type">
     <meta content="utf-8" http-equiv="encoding">
      <title>{1}</title>
      {2}
      {3}
    </head>
    <body>
    <table style='width:100%; border-collapse: collapse;'>
     <tr>
      <td style='padding: 0px; width:50px'><img src='../../img/icons/science2.png' style='height:35px'></td>
      <td style='padding: 0px; text-align: left;'>PyLIMS</td>
      <td style='padding: 0px; text-align: right; width:50%'>
         <a id='cgi_log'></a> &nbsp; &nbsp;
         <a id='login_info'></a>
      </td>
     </tr>
    </table>
    '''.format(cookiesToSet.output().strip(), page_title, js_code, css_code)

    # Present the login screen if the user can not be identified from LIMS cookies or a login attempt   

    if 'user_id' not in Data.cgiVars:
        s = '''\
        <br>
            <table style='border-collapse: collapse;'>
             <tr style='vertical-align:top'>
              <td style='padding: 0px; width:50px; text-align: left;'>
                <img src ='../../img/icons/small57.png' style='height:30px'>
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
        ''' % calling_file

        print(textwrap.dedent(html_header).strip())
        print(textwrap.dedent(s).strip())

        exit()
    else:
        # User successfully logged in via cookie
        print(textwrap.dedent(html_header).strip())

        # Update interface header with login info
        s = '(<u><a href=\'{0}\'>Log</a></u>)'.format(Data.cgiVars['cgi_log_file'])
        print("<script>document.getElementById('cgi_log').innerHTML=\"{0}\"</script>\n".format(s))

        # Update interface header with login info
        s = '{0} (<u><a onClick=\'PyLIMS_logout()\'>logout</a></u>)'.format(Data.cgiVars['user_id'])
        print("<script>document.getElementById('login_info').innerHTML=\"{0}\"</script>\n".format(s))

    return

def end_cgi_page():
    print('</body></html>')

def create_randomized_id(length=5, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(length))

def create_sequence_digest(sequence):
    hash = hashlib.sha1()
    hash.update(sequence.encode('utf-8'))
    return hash.hexdigest()

def update_cgi_log(update_type, text):
    ts = strftime("%Y-%m-%d %I:%M%p", gmtime())

    # Color code log enteries according to provided update_type
    text_color = '#000000'
    text_colors = {'page_start':'#00A300', 'information':'#0052A3', 'warning':'#B2B200', 'error':'#FF0000'}
    if update_type in text_colors:
        text_color = text_colors[update_type]

    # Use the last three directories in the full script path to identify the script in the log file
    path_array = sys.argv[0].split('/')
    report_path = '/'.join(path_array[len(path_array)-3:])
    log_tag = '[' + '<font color="{0}">'.format(text_color) + report_path +' '+ ts + '</font>]<br>'

    # If log file exists -- add the update text. If the file does not exist, print a HTML header then the update text.
    if os.path.isfile(Data.cgiVars['cgi_log_file']):
        with open(Data.cgiVars['cgi_log_file'], "a") as cgi_log_file:
            cgi_log_file.write(log_tag + text + "<br><br>\n")
    else:
        html_header = '''\
                 <html>
                  <head>
                   <title>CGI log</title>
                  </head>
                  <body style='font-family:"Courier New", Courier, monospace'; font-size:8px'>
                 '''
        with open(Data.cgiVars['cgi_log_file'], 'w') as cgi_log_file:
            cgi_log_file.write(textwrap.dedent(html_header))
            cgi_log_file.write(log_tag + text + "<br><br>\n")