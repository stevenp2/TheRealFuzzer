import csv
import random

# NOTE: content is in the form  [[word1, word2, 3], [nextline, abd, so], [forth, 1, 1]]
def read_csv_input(text_input):
    sniffer = csv.Sniffer()
    delimiter = ',' # by default
    content = ''
 
    with open(text_input) as f:
        csv_file = sniffer.sniff(f.read(1024))
        delimiter = csv_file.delimiter

        f.seek(0)
        content = f.read()

    return content, delimiter 
    
# Simple strategy - have fun with delimiters
def vary_delimiters(Runner, content, delimiter):

    try_delimiters = ['|', 'a', '', '@', '🐒', 'word', '水']

    for d in try_delimiters:
        result = content.replace(delimiter, d)
        if Runner.run_process(result):
            return result
        
# Simple strategy - expand file size
def expand_file(Runner, content, delimiter):
    content = ''
    result = ''

    for i in range (0,50):
        result += content
        if Runner.run_process(result):
            return result

