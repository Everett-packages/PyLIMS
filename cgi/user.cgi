#!C:\Python34\python.exe
import argparse
import textwrap
import sys
sys.path.append("../lib")

import LimsCore

LimsCore.start_cgi_page()

db = LimsCore.LimsDB('lims_admin', 'pa!#%', 'pylims')
privileges = db.privileges()
print('pp', privileges)

print("\n\n")

db = LimsCore.LimsDB('lims_test', 'pt!#%', 'pylims')
privileges = db.privileges()
print('pp', privileges)


print ('F1: ', LimsCore.Data.cgi)

#r = db.fetchall("select * from protein")
#for a in r:
#  print(a['protein_id'])

db.privileges()

db.disconnect()


# JKE