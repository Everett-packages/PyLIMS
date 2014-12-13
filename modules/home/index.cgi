#!/usr/bin/python3
import sys
sys.path.append("../../lib")
import LimsCore

# Start the CGI page
LimsCore.start_cgi_page()


html = '''\
       <br>
       Welcome to PyLIMS.<br><br>


    '''

print(html)