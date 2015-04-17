import sys
import hashlib
import string
import random
import subprocess
import time
import xmltodict
import re

def create_randomized_id(length=5, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(length))


def create_sequence_digest(sequence):
    seq_hash = hashlib.sha1()
    seq_hash.update(sequence.encode('utf-8'))
    return seq_hash.hexdigest()


def pf(s):
    """ pf( [string] ) is a short hand function for both printing to stdout and flushing the stdout buffer
        to ensure that printed text is printed to the browser as soon as possible. """

    print(s)
    sys.stdout.flush()


def config_data():
    with open('../../config.xml') as x:
        xml = x.read()
    config = xmltodict.parse(xml)
    return config

def next_record_id(db, table, id):
    record_prefixes = {}
    record_prefixes['DNA'] = 'PRO'
    record_prefixes['PROTEIN'] = 'PRO'
    record_prefixes['EXPRESSION'] = 'EXP'
    record_prefixes['PURIFICATION'] = 'PUR'
    record_prefixes['HSQC'] = 'HSQC'
    record_prefixes['NMR'] = 'NMR'

    numbers = [0]
    for r in db.fetchall("select {0} from {1}".format(id, table)):
        m = re.search(r'(\d+)$', r[id], re.M | re.I)
        if m:
            numbers.append(int(float(m.group(1))))
    numbers = sorted(numbers)

    return record_prefixes[table.upper()] + "-{0:010d}".format(numbers.pop() + 1)

def execute_commands(command_array, wait=True):
    """ This function invokes he subprocess.Popen method to run system commands which are provided
        as a lists of lists, ie.   [ [ 'a.py',  '-f', 'file_name' ], [ 'b.py', '-j', '10' ] ]
        Commands are executed in the order that they are found in the list of lists and the function
        will wait for them to conclude and return their results as a list of lists.   The first element
        of each list will be the stdout output and the second element will be the stderr output from
        executed commands. The HUD status icon will be updated to the 'working' icon until all commands
        have been executed. Commands will be ran in the background if the optional function parameter 'wait'
        is set to False and the stderr and stdout results will not be returned.
    """
    command_results = []

    for command in command_array:

        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if wait:
            while p.poll() is None:
                time.sleep(1)

            command_results.append([p.stdout.read().decode('UTF-8'), p.stderr.read().decode('UTF-8')])
        else:
            command_results.append(['NA', 'NA'])

    return command_results