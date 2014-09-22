#!/usr/bin/python3
import textwrap
import time
import sys

html_header = '''\
    Content-type: text/html

    <html>
     <head>
     <meta content="text/html;charset=utf-8" http-equiv="Content-Type">
     <meta content="utf-8" http-equiv="encoding">
      <title>test</title>

    </head>
    <body>
'''

#sys.stdout.write(textwrap.dedent(html_header).strip())
print(textwrap.dedent(html_header).strip())

for x in range(5):
    print('done<br>')
    sys.stdout.flush()
    time.sleep(1)

