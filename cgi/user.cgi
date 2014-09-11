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

print("\n\n")


print ('F1: ', LimsCore.Data.cgi)

#r = db.fetchall("select * from protein")
#for a in r:
#  print(a['protein_id'])

db.privileges()

db.disconnect()


# JKE