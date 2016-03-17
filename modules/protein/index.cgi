#!/usr/bin/python3
import sys
sys.path.append("../../lib")
import LimsCGI
import LimsDB
import LimsTools
import re
from Bio.Seq import Seq
from Bio.Alphabet import IUPAC

# Start the CGI page
LimsCGI.start_cgi_page()

# Connect to MySQL database
# Connection credentials are taken form the login form created by start_cgi_page() or extracted from existing cookies
db = LimsDB.DB(LimsCGI.Data.cgiVars['user_id'], LimsCGI.Data.cgiVars['user_passwd'],
               LimsCGI.Data.cgiVars['database_name'])

# Determine the privileges that this user has
privileges = db.privileges()

# determine the name of this script
m = re.search(r'([^/]+)$', __file__)
script_file_name = m.group(1)


def submit_create_protein_record_request():

    data_items_list = []
    for d in LimsCGI.Data.cgiVars['protein_data'].upper().split("\n"):
        data_items = {}
        for dd in d.split():
            if ':' not in dd:
                LimsCGI.cgi_error_message("Data item '{0}' does not contain a label followed by a colon.".format(dd))


            label, data = re.compile(r'\s*:\s*').split(dd)
            data_items[label] = data

        if 'DNA' not in data_items:
            LimsCGI.cgi_error_message("The 'dna:' data label was not present in the provided data line:<br>{0}".format(d))

        data_items_list.append(data_items)

    line_n = 1
    for d in data_items_list:
        print("Processing data line {0}<br>".format(line_n))
        line_n += 1

        protein_nt_sequence = Seq(d['DNA'], IUPAC.unambiguous_dna)

        protein_aa_sequence = ''
        try:
            protein_aa_sequence = protein_nt_sequence.translate()
        except:
            LimsCGI.cgi_error_message("The provided DNA sequence could not be translated.")

        # remove terminal stop codon(s) from both the provided DNA sequence and the translated DNA sequence
        m = re.search('([\*]+)$', str(protein_aa_sequence))
        if m:
            protein_nt_sequence = protein_nt_sequence[:-3*len(m.group(0))]
            protein_aa_sequence = protein_aa_sequence[:-len(m.group(0))]

        # test for internal stop codons
        m = re.search('\*', str(protein_aa_sequence))
        if m:
            LimsCGI.cgi_error_message("The translated DNA sequence contains an internal stop codon.")

        sql = "insert into protein (protein_id, protein_sequence, sequence_digest) values ('{0}', '{1}', '{2}')" \
              .format(LimsTools.next_record_id(db, 'protein', 'protein_id'), protein_aa_sequence,
                      LimsTools.create_sequence_digest(str(protein_aa_sequence)))

        print('sql: |{0}|<br>'.format(sql))
        #db.execute(sql)


def create_protein_record():

    html = '''
    <br>
    Enter DNA sequence encoding targeted protein sequence:<br>
    <form accept-charset="UTF-8" action="{0}" method="post">
    <textarea name='protein_data' style='width:500px;height:100px;padding:2px;font-family:arial;font-size:10pt'>
    </textarea>

    <br>
    <input type='hidden' name='action' value='submit_create_protein_record_request'>
    <input type='submit' value='create record'>
    </form>
    <script>database_change('protein_sequence_database', 'protein_database_id')</script>

    '''.format(script_file_name)

    print(html)

def cgi_actions():
    if 'action' in LimsCGI.Data.cgiVars:
        if LimsCGI.Data.cgiVars['action'] in globals():
            globals()[LimsCGI.Data.cgiVars['action']]()
        else:
            print("Error: CGI action variable '{0}' does not map to a PyLIMS function."
                  .format(LimsCGI.Data.cgiVars['action']))
            exit()
    else:
        # Default action code ...
        print("Error: This module required that the CGI variable 'action' be defined.")
        exit()

cgi_actions()

exit()
