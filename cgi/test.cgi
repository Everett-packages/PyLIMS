#!/usr/bin/python3
import argparse
import textwrap
import sys
sys.path.append("../lib")
from pprintpp import pprint as pp

import LimsCore

LimsCore.start_cgi_page()

db = LimsCore.LimsDB('admin', 'admin1', 'pylims_dev')
privileges = db.privileges()
print('pp', privileges)

print("<br><br>")

id = LimsCore.create_randomized_id(25)
print("Random id: ", id, "<br>")

id = LimsCore.create_randomized_id(25, 'abc123')
print("Random id: ", id, "<br>")

sequence = 'MHREWQPLKSCNMEADFTY'
digest = LimsCore.create_sequence_digest(sequence)
print("Digest of sequence: ", sequence, " -> ", digest, "<br><br>\n")

print ('Data.cgiVars: ', LimsCore.Data.cgiVars, "<br><br>")

#r = db.fetchall("select * from protein")
#for a in r:
#  print(a['protein_id'])

db.privileges()


print("Log:<br>", LimsCore.Data.log,"<br><br>\n")

pp(LimsCore.Data.tr)

db.disconnect()


# JKE