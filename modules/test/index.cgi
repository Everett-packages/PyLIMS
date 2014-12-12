#!/usr/bin/python3
import sys

sys.path.append("../../lib")
import LimsCore
from pprintpp import pprint as pp
from Bio.SeqUtils.ProtParam import ProteinAnalysis

# Start the CGI page
LimsCore.start_cgi_page()

# Write to the CGI log which is accessible from the top of page headers
LimsCore.update_cgi_log('information', 'update 1')

# Connect to MySQL database
# Connection credentials are taken form the login form created by start_cgi_page or extracted from existing cookies
db = LimsCore.LimsDB(LimsCore.Data.cgiVars['user_id'], LimsCore.Data.cgiVars['user_passwd'],
                     LimsCore.Data.cgiVars['database_name'])

# Determine the privileges that this user has
privileges = db.privileges()
print('db privileges', pp(privileges), "<br><br>")

# Create random ids
id = LimsCore.create_randomized_id(25)
print("Random id (25 char): ", id, "<br>")

id = LimsCore.create_randomized_id(25, 'abc123')
print("Random id (25 char w/ limited chars): ", id, "<br><br>")

print("<form action='http://google.com'><input name='test'><input type='submit'></form>\n")

# Protein sequence digests
sequence = 'MHREWQPLKSCNMEADFTY'
digest = LimsCore.create_sequence_digest(sequence)
print("Digest of sequence: ", sequence, " -> ", digest, "<br><br>\n")

# CGI variables
print('Data.cgiVars: ', LimsCore.Data.cgiVars, "<br><br>")

# Configuration variables
print('Configuration variables: ')
pp(LimsCore.config)
print('<br><br>')

# BioPython

seq = 'MSWMQNLKNYQHLRDPSEYMSQVYGDPLAYLQETTKFVTEREYYEDFGYGECFNSTESEVQCELITGEFDPKLLPYDKRLAWHFKEFCYKTSAHGIPMIGEAP'
print('protein sequence: ' + seq + '<br><br>')
pa = ProteinAnalysis(seq)
print("MW: ", "%.2f" % pa.molecular_weight(), '<br><br>')

# Invoke jackhmmer
work_dir = '../../data/tmp_data/' + LimsCore.Data.cgiVars['session_id']

with open(work_dir + '/seq.ff', 'w') as s:
    s.write(">seq\n{0}".format(seq))

print('Running jackhmmer...<br>')

comm = [
         [ LimsCore.config['LIMS']['software']['jackhmmer'], '--tblout', work_dir+'/seq.tbl',
           '--domtblout', work_dir+'/dom.tbl', '-E', '1.0', '--incE', '0.01',
           work_dir+'/seq.ff', LimsCore.config['LIMS']['databases']['UniProtSwprt']
         ]
       ]

r = LimsCore.execute_commands(comm)
print('result (list of lists) [0]->stdout [1]->stderr: <br>')
pp(r)



db.disconnect()
