#!C:\Python34\python.exe
import textwrap
import sys
sys.path.append("../lib")
import LimsCore

LimsCore.start_cgi_page()

if 'action' in LimsCore.Data.cgi:
    print(LimsCore.Data.cgi['action'].value)

exit()
