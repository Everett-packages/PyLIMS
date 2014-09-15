#!/usr/bin/python3
import sys
sys.path.append("../lib")
import LimsCore

# Start the CGI page
LimsCore.start_cgi_page()

# Write to the CGI log which is accessible from the top of page headers
LimsCore.update_cgi_log('update 1')

# Connect to MySQL database
# Connection credentials are taken form the login form created by start_cgi_page or extracted from existing cookies
db = LimsCore.LimsDB(LimsCore.Data.cgiVars['user_id'], LimsCore.Data.cgiVars['user_passwd'], LimsCore.Data.cgiVars['database_name'])

# Determine the privileges that this user has
privileges = db.privileges()
print('db privileges', privileges, "<br><br>")

# Create random ids
id = LimsCore.create_randomized_id(25)
print("Random id (25 char): ", id, "<br>")

id = LimsCore.create_randomized_id(25, 'abc123')
print("Random id (25 char w/ limited chars): ", id, "<br><br>")

# Protein sequence digests
sequence = 'MHREWQPLKSCNMEADFTY'
digest = LimsCore.create_sequence_digest(sequence)
print("Digest of sequence: ", sequence, " -> ", digest, "<br><br>\n")

# CGI variables
print ('Data.cgiVars: ', LimsCore.Data.cgiVars, "<br><br>")


db.disconnect()


# JKE