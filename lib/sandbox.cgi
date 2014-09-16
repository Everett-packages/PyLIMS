#!/usr/bin/python3
import cgitb
import cgi
import argparse
import pymysql
import textwrap
import hashlib
import os
from Bio.SeqUtils.ProtParam import ProteinAnalysis

argParser = argparse.ArgumentParser()
argParser.add_argument('-protein_sequence', metavar='', help='protein amino acid sequence')
argParser.add_argument('-debug', action='store_true', help='display debuging log text')
args = argParser.parse_args()

# determine incoming protein sequence from either the command line or CGI arguments

if 'GATEWAY_INTERFACE' in os.environ and 'protein_sequence' in form:   
    protein_sequence = form['protein_sequence'].value
elif args.protein_sequence:
    protein_sequence = args.protein_sequence
else:
    protein_sequence = ''

protein_sequence = 'ACNMREWTRWQ'

protein_sequence_stats = ProteinAnalysis(protein_sequence)
mw = protein_sequence_stats.molecular_weight()
print ("f1", mw )
print ("f2", protein_sequence_stats.molecular_weight() )
