import textwrap
import os
import sys
import inspect
import re
import xmltodict
import time
import pymysql
import hashlib
import string
import random
import subprocess
from http import cookies
# from pprintpp import pprint as pp


def pf(s):
    """ pf( [string] ) is a short hand function for both printing to stdout and flushing the stdout buffer
        to ensure that printed text is printed to the browser as soon as possible. """

    print(s)
    sys.stdout.flush()


class DataClass:
    cgiVars = {}
    pass

# Global NameSpace to convey data to the calling module
Data = DataClass()

# read in config xml and convert xml to an object
# ie.  config['LIMS']['software']['blast'] = path to local blast installation

with open('../../config.xml') as x:
    xml = x.read()
    config = xmltodict.parse(xml)


class LimsDB:
    """ The LimsDB class connects to a MySQL database with the provided credentials, provides a number
        of methods for interacting with the database and provides additional methods to determine a users
        level of access to the database. """

    def __init__(self, user_id, user_passwd, database_name):

        # connect to the database and define a cursor
        connection_credentials = {'user': user_id, 'passwd': user_passwd, 'host': 'localhost', 'port': 3306,
                                  'db': database_name}

        try:
            self.conn = pymysql.connect(**connection_credentials)
            self.cur = self.conn.cursor(pymysql.cursors.DictCursor)
        except:
            error_msg = "Error.<br>Could not connect to the database '{0}' using user id '{1}' with password '{2}'". \
                format(database_name, user_id, user_passwd)
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


def execute_commands(command_array, wait=True):
    """ This function invokes he subprocess.Popen method to run system commands which are provided
        as a lists of lists, ie.   [ [ 'a.py',  '-f', 'file_name' ], [ 'b.py', '-j', '10' ] ]
        Commands are executed in the order that they are found in the list of lists and the function
        will wait for them to conclude and return their results as a list of lists.  The first element
        of each list will be the stdout output and the second element will be the stderr output from
        executed commands. Commands will be ran in the background if the optional function paramater 'wait'
        is set to False and stderr and stdout results will not be returned.
    """
    command_results = []

    pf("<script>HUD_set_status_working()</script>\n")

    for command in command_array:

        update_cgi_log('information', 'staring command: (wait: ' + str(wait) + ') ' + ' '.join(command))
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if wait:
            update_cgi_log('information', 'waiting for command to complete ...')

            while p.poll() is None:
                time.sleep(1)

            command_results.append([p.stdout.read().decode('UTF-8'), p.stderr.read().decode('UTF-8')])
            update_cgi_log('information', 'command complete')
        else:
            command_results.append(['NA', 'NA'])

    pf("<script>HUD_set_status_idle()</script>\n")

    return command_results


def start_cgi_page(page_title='untitled'):
    import cgitb
    import cgi

    cgitb.enable(display=1, logdir="tmp")

    # Make cgi.FieldStorage available to the calling script via the Data name space
    Data.cgi = cgi.FieldStorage()

    # Store variable, value pairs from cgi.FieldStorage in Data.cgiVars dict for easy access and manipulation
    Data.cgiVars = {'cgi_log_file': '/dev/null'}
    for v in Data.cgi:
        Data.cgiVars[v] = Data.cgi[v].value

    # parse cookies
    parsed_cookies = {}
    cookies_to_set = cookies.SimpleCookie()

    if 'HTTP_COOKIE' in os.environ:
        cookie_list = os.environ['HTTP_COOKIE'].split(';')

        for cookie in cookie_list:
            cookie_var, cookie_value = cookie.split('=')
            parsed_cookies[cookie_var.strip()] = cookie_value.replace('"', '').strip()

    # CGI session id
    # Create a new session id. Use existing session id if found in cookies.

    Data.cgiVars['session_id'] = create_randomized_id(10)

    if 'session_id' in parsed_cookies:
        Data.cgiVars['session_id'] = parsed_cookies['session_id']

    # CGI log
    # Each user will have a log file used primarily for debugging purposes.
    # The name of the log file will be tracked with cookies and a new log file name
    # will be created if an existing log file name is not found in the user's cookies.

    Data.cgiVars['cgi_log_file'] = "../../data/tmp_data/" + Data.cgiVars['session_id'] + "/cgi.log.html"

    if os.path.isdir("../../data/tmp_data/" + Data.cgiVars['session_id']) is False:
        os.mkdir("../../data/tmp_data/" + Data.cgiVars['session_id'])

    # Start the log for this CGI page

    update_cgi_log('page_start', "starting page")

    # Specific variables need to be stored in both Data.cgiVars and http cookies.
    # If a variable is found in Data.cgiVars but not stored as a cookie then set the cookie
    # If a variable is found in a cookie but not already stored in Data.cgiVars then store the variable in Data.cgiVars

    cookie_variables = ['user_id', 'user_passwd', 'database_name', 'session_id']
    for v in cookie_variables:
        if v in Data.cgiVars and v not in parsed_cookies:
            cookies_to_set[v] = Data.cgiVars[v]
            cookies_to_set[v]["path"] = "/"
        elif v in parsed_cookies and v not in Data.cgiVars:
            Data.cgiVars[v] = parsed_cookies[v]
        else:
            pass

    # Determine the name of the script calling this module and determine if there is a corresponding
    # .js file.  ie.  protein.cgi call this module then check for protein.js
    # If the file exists then add a line to the header to import the js file and then print the HTML header.
    # Do the same for .css files then print the default LIMS header including the relevant js and css code.

    # determine the name of the script calling this module
    m = re.search(r'([^/]+)$', inspect.stack()[1][1], re.M | re.I)
    calling_file = m.group(1)

    # determine the path of this module
    Data.cgiVars['module_file_dir'] = os.path.dirname(__file__)

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

    # Create JS code that defines a JS object that stores variables in Data.cgiVars so that JS scripts
    # can have access this these variables once the Python CGI scripts exit.

    js = ''
    for v in Data.cgiVars:
        js += 'pylims.cgiVars.' + v + ' = \'' + Data.cgiVars[v] + '\';\n'

    js_pylims_obj_code = '''<script>
                              pylims = {{}};
                              pylims.cgiVars = {{}};
                              {0}
                           </script>'''.format(js)

    # Assemble the HTML header
    # The Heads Up Display (HUD) icons are loaded after the top of the page is rendered so that that developers
    # can dynamically change or omitt the icons as needed. There are a number of JS functions in js/all.js available
    # for manipulating these icons.

    # sf dictionary used to fromat the html header
    sf = {'cookies': cookies_to_set.output().strip(), 'title': page_title, 'js_code': js_code, 'css_code': css_code,
          'module_file_dir': Data.cgiVars['module_file_dir'], 'calling_file': calling_file, 'js_pylims_obj_code':
          js_pylims_obj_code}

    html_header = '''
    {cookies}
    Content-type: text/html

    <html>
     <head>
     <meta content="text/html;charset=utf-8" http-equiv="Content-Type">
     <meta content="utf-8" http-equiv="encoding">
      <title>{title}</title>
      {js_pylims_obj_code}
      <script type='text/javascript' src='{module_file_dir}/js/all.js'></script>
      {js_code}
      {css_code}
    </head>
    <body>
    <table style='width:100%; border-collapse: collapse;'>
     <tr>
      <td style='padding: 0px; width:50px'><img src='{module_file_dir}/img/pylims1.png' style='height:35px'></td>
      <td align='left' style='padding: 0px; text-align: left '>PyLIMS</td>
      <td align='right' style='padding: 0px; text-align: right;>
         <div id='HUD'>
           <span id='HUD_search'></span>
           <span id='HUD_menu'></span>
           <span id='HUD_log'></span>
           <span id='HUD_logout'></span>
           <span id='HUD_status'></span>
         </div>
      </td>
     </tr>
    </table>
    <hr style='height: 0px; margin: 0px; border-bottom: 1px solid #000000; font-size: 0.5px'><br>
    '''.format(**sf)

    # Present the login screen if the user can not be identified from LIMS cookies or a login attempt   

    if 'user_id' not in Data.cgiVars:
        s = '''\
        <br>
            <table style='border-collapse: collapse;'>
             <tr style='vertical-align:top'>
              <td style='padding: 0px; width:50px; text-align: left;'>
                <img src ='{module_file_dir}/img/lock1.png' style='height:30px'>
              </td>
              <td style='text-align: left;'>PyLIMS is restricted to registered users.<br>Please sign in.</td>
              <td style='width:10px'></td>
              <td style='padding: 0px; text-align: left;'>
                <form name="login" accept-charset="UTF-8" action="{calling_file}" method="post">
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
        '''.format(**sf)

        print(textwrap.dedent(html_header).strip())
        print(textwrap.dedent(s).strip())

        exit()
    else:
        # User successfully logged in via cookie
        print(textwrap.dedent(html_header).strip())

        pf("<script>HUD_load_default_buttons()</script>")


def end_cgi_page():
    print('</body></html>')


def create_randomized_id(length=5, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(length))


def create_sequence_digest(sequence):
    seq_hash = hashlib.sha1()
    seq_hash.update(sequence.encode('utf-8'))
    return seq_hash.hexdigest()


def update_cgi_log(update_type, text):
    ts = time.strftime("%Y-%m-%d %I:%M%p", time.gmtime())

    # Color code log enteries according to provided update_type
    text_color = '#000000'
    text_colors = {'page_start': '#00A300', 'information': '#0052A3', 'warning': '#B2B200', 'error': '#FF0000'}
    if update_type in text_colors:
        text_color = text_colors[update_type]

    # Use the last three directories in the full script path to identify the script in the log file
    path_array = sys.argv[0].split('/')
    report_path = '/'.join(path_array[len(path_array) - 3:])
    log_tag = '[' + '<font color="{0}">'.format(text_color) + report_path + ' ' + ts + '</font>]<br>'

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