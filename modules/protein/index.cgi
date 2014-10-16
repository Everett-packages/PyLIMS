#!/usr/bin/python3
import sys
sys.path.append("../../lib")
import LimsCore
import re

# Start the CGI page
LimsCore.start_cgi_page()

# Connect to MySQL database
# Connection credentials are taken form the login form created by start_cgi_page or extracted from existing cookies
db = LimsCore.LimsDB(LimsCore.Data.cgiVars['user_id'], LimsCore.Data.cgiVars['user_passwd'],
                     LimsCore.Data.cgiVars['database_name'])

# Determine the privileges that this user has
privileges = db.privileges()

# determine the name of this script
m = re.search(r'([^/]+)$', __file__)
script_file_name = m.group(1)


def main():
    cgi_actions()


def cgi_actions():
    if 'action' in LimsCore.Data.cgiVars:
        if LimsCore.Data.cgiVars['action'] in globals():
            # noinspection PyCallingNonCallable
            globals()[LimsCore.Data.cgiVars['action']]()
        else:
            print("Error: CGI action variable '{0}' does not map to a PyLIMS function."
                  .format(LimsCore.Data.cgiVars['action']))
            exit()
    else:
        print("Error: CGI variable 'action' not defined.")
        exit()


def create_protein_record():

    html = '''
    <br>
    Enter DNA sequence encoding targeted protein sequence:<br>
    <form accept-charset="UTF-8" action="{0}" method="post">
    <textarea name='protein_nt_sequence' style='width:500px;height:100px;padding:2px;font-family: arial; font-size:10pt'>
    </textarea>
    <br>
    <br>
    DNA annotation.<br>
    Database name:
    <select id='dna_sequence_database' onChange="database_change('dna_sequence_database', 'dna_database_id')")>
       <option value='designed sequence' selected>designed sequence</option>
       <option value='GenBank'>GenBank</option>
       <option value='NCBI Gene'>NCBI Gene</option>
    </select> &nbsp; &nbsp;
    <span id='dna_database_id' style='visibility:hidden'>
     Database id: <input name='dna_sequence_database_id' type='text' style='width:100px'>
    </span>
    <script>database_change('dna_sequence_database', 'dna_database_id')</script>
    '''.format(script_file_name)

    print(html)

main()

exit()
