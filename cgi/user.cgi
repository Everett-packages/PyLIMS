#!/usr/bin/python3
import argparse
import textwrap
import sys
sys.path.append("../lib")

import LimsCore

LimsCore.start_cgi_page()

db = LimsCore.LimsDB('admin', 'admin1', 'pylims_dev')
privileges = db.privileges()
print('pp', privileges)

print("<br><br>")


print ('Data.cgi: ', LimsCore.Data.cgi, "<br><br>")

print ('Data.log: ', LimsCore.Data.log, "<br><br>")

#r = db.fetchall("select * from protein")
#for a in r:
#  print(a['protein_id'])

db.privileges()

db.disconnect()


# JKE