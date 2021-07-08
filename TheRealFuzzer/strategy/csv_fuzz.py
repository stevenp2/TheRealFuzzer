import csv
import random
import re
from .bad_stuff import bad_integers

# NOTE: content is in the form  [[word1, word2, 3], [nextline, abd, so], [forth, 1, 1]]
def _read_csv_input(content):
    try:
        sniffer = csv.Sniffer()
        csv_file = sniffer.sniff(content)
        delimiter = csv_file.delimiter
        return content, delimiter 
        
    except:
        return content, None
    
# Simple strategy - have fun with delimiters
def vary_delimiters(Runner, content):
    content, delimiter = _read_csv_input(content)

    if delimiter == None:
        return

    try_delimiters = ['|', 'a', '', '@', '🐒', 'word', '水', '水水水']

    for d in try_delimiters:
        payload = content.replace(delimiter, d)
        if Runner.run_process(payload):
            return payload
        
# Simple strategy - expand file size from empty
def expand_file(Runner, content):
    payload = ''

    # Empty file
    run = Runner.run_process(payload)
    if run:
        if run[0]:
            return payload

    for i in range (0,50):
        payload += content
        run = Runner.run_process(payload)
        if run: 
            if run[0]:
                return payload

# Simple strategy - expand file size from empty
def negate_everything(Runner, content):
    c = csv.reader(content)
    payload = []
    for row in c:
        payload_row = []
        for row_elem in row:
            new_value = bytearray(row_elem, 'utf-8')
            new_value = ''.join([chr(item ^ 255) for item in new_value])

            payload_row.append(new_value)

        payload.append(payload_row)
    
    # Convert to csv
    payload_csv = ''
    for row in payload:
        payload_csv += ','.join(row) + '\n'

    if Runner.run_process(payload_csv):
        return payload_csv

def oob_ints(Runner, content):
    # regex
    integers = re.findall(r'[0-9]+', content)

    def process_func(Runner, content, possible_int):

        for integer in integers:
            content = content.replace(integer, str(possible_int))

        return content

    for bad_int in bad_integers():
        payload = process_func(Runner, content, bad_int)
        if Runner.run_process(payload):
            return payload

# randomly flips some bits in string
def bit_flip(Runner, content):

    for j in range(0, 300):

        byte_str = bytearray(content, 'utf-8')

        for i in range(0, len(byte_str)):
            if random.randint(0, 2) == 1:
                byte_str[i] ^= random.getrandbits(7)


        payload = byte_str.decode('ascii')

        if Runner.run_process(payload):
            return payload
