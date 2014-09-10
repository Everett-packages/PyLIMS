#!/home1/helixsc1/usr/local/bin/python3
import cgitb
import cgi
import argparse
import pymysql
import textwrap
import hashlib
import os
from Bio.SeqUtils.ProtParam import ProteinAnalysis

with open(js_file) as x: js_code = x.read()

expires = time.time() + int(config['PyL']['login_persistence']) * 3600
    expires_text = time.strftime("%a, %d-%b-%Y %T GMT", time.gmtime(expires))


    #
    # c = 'Set-Cookie: user_id=test; expires=Thu, 18 Dec 2013 12:00:00 GMT'; print(c)

argParser = argparse.ArgumentParser()
argParser.add_argument('-protein_sequence', metavar='', help='protein amino acid sequence')
argParser.add_argument('-debug', action='store_true', help='display debuging log text')
args = argParser.parse_args()

cgitb.enable(display=1, logdir="tmp")
form = cgi.FieldStorage()


test = 'abc'
array = list(test)
print(array)

# determine incoming protein sequence from either the command line or CGI arguments

if 'GATEWAY_INTERFACE' in os.environ and 'protein_sequence' in form:   
    protein_sequence = form['protein_sequence'].value
elif args.protein_sequence:
    protein_sequence = args.protein_sequence
else:
    protein_sequence = ''

protein_sequence_stats = ProteinAnalysis(protein_sequence)
mw = protein_sequence_stats.molecular_weight()
print ("f1", mw )
print ("f2", protein_sequence_stats.molecular_weight() )


# generate a 40 character sha1 hash hex value for the protein sequence

protein_sequence_digest_hash = hashlib.sha1()
protein_sequence_digest_hash.update(protein_sequence.encode('utf-8'))
protein_sequence_digest = protein_sequence_digest_hash.hexdigest()


conn = pymysql.connect(read_default_file='./.mysql.pppPb')
cur = conn.cursor();

def html_header( page_title ):
    s = '''\
    Content-type: text/html

    <html>
     <head>
      <title>%(page_title)s</title>
    </head>
    <body>
    ''' % { 'page_title': page_title }
    print(textwrap.dedent(s))
    return

html_header( 'protein' )


print("</html>")
