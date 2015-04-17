from LimsTools import create_randomized_id, pf
import textwrap
import os
import re
import sys
import inspect
import cgitb
import cgi
import time
from http import cookies


class DataClass:
    cgiVars = {}
    pass

# Global NameSpace to convey data to the calling module
Data = DataClass()

def start_cgi_page(page_title='untitled'):

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
    # .js file.  ie.  protein.cgi call this module then check for index.js
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

    # read menu html from local file
    with open(Data.cgiVars['module_file_dir'] + '/' + 'html/menu1.html', "r") as myfile:
        menu_html = myfile.read().replace('\n', '')

    # sf dictionary used to format the html header
    sf = {'cookies': cookies_to_set.output().strip(), 'title': page_title, 'js_code': js_code, 'css_code': css_code,
          'module_file_dir': Data.cgiVars['module_file_dir'], 'calling_file': calling_file, 'js_pylims_obj_code':
          js_pylims_obj_code, 'main_menu_html': menu_html}

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
      <td align='right' style='padding: 0px; text-align: right'>
         <div id='HUD'>
           <span id='search'></span>
           <span id='menu'></span>
           <span id='log'></span>
           <span id='logout'></span>
           <span id='status'></span>
         </div>
      </td>
     </tr>
    </table>
    <hr style='height: 0px; margin: 0px; border-bottom: 1px solid #000000; font-size: 0.5px'>
    <div id='menu_overlay' style='position:absolute;width:100%;height:100%;z-index:10;background: rgba(255,255,255,0.9);visibility:hidden'>{main_menu_html}</div>
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
                   <tr style='vertical-align:top'>
                     <td><input type='submit' value='log in'></td>
                   </tr>
                  </table>

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

        load_default_buttons()


def set_status_working():
    pf("<script>document.getElementById('status').innerHTML = \"<img src='" + Data.cgiVars['module_file_dir'] +
       "/img/animated_working.gif'>\"</script>\n")


def set_status_idle():
    pf("<script>document.getElementById('status').innerHTML = \"<img src='" + Data.cgiVars['module_file_dir'] +
        "/img/status_idle.png'>\"</script>\n")


def load_logout_button():
    pf("<script>document.getElementById('logout').innerHTML = \"<a onClick='user_logout()'><img src='" +
       Data.cgiVars['module_file_dir'] + "/img/logout.png'></a>\"</script>\n")


def load_log_button():
    pf("<script>document.getElementById('log').innerHTML = \"<a href='" + Data.cgiVars['cgi_log_file'] +
       "'><img src='" + Data.cgiVars['module_file_dir'] + "/img/CGI_log.png'></a>\"</script>\n")


def load_menu_button():
    pf("<script>document.getElementById('menu').innerHTML = \"<img src='" + Data.cgiVars['module_file_dir'] +
       "/img/menu.png' onClick='show_main_menu()'>\"</script>\n")


def load_search_button():
    pf("<script>document.getElementById('search').innerHTML = \"<img src='" + Data.cgiVars['module_file_dir'] +
       "/img/search.png'>\"</script>\n")


def load_default_buttons():
    set_status_idle()
    load_logout_button()
    load_log_button()
    load_menu_button()
    load_search_button()


def end_cgi_page():
    print('</body></html>')


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