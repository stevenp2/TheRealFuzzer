import csv
import random

# NOTE: content is in the form  [[word1, word2, 3], [nextline, abd, so], [forth, 1, 1]]
# def read_csv_input(text_input):
#     sniffer = csv.Sniffer()
#     content = []
#     delimiter = ',' # by default
 
#     with open(text_input) as f:
#         csv_file = sniffer.sniff(f.read(1024))
#         delimiter = csv_file.delimiter

#         f.seek(0)
#         reader = csv.reader(f, delimiter=delimiter)

#         for row in reader:
#             content.append(row)

#     return content, delimiter 
    
# Simple strategy - have fun with delimiters
def vary_delimiters(Runner, text_input):
    csv_return = ''
    delimiter = ',' # by default
    sniffer = csv.Sniffer()

    with open(text_input) as f:
        csv_file = sniffer.sniff(f.read(1024))
        delimiter = csv_file.delimiter

        f.seek(0)
        csv_return = f.read()    

    try_delimiters = ['|', 'a', '', '@', '🐒', 'word', '水']

    for d in try_delimiters:
        result = csv_return.replace(delimiter, d)
        if Runner.run_process(result):
            return result
        
# Simple strategy - expand file size
def expand_file(Runner, text_input):
    csv = ''
    result = ''
    with open(text_input) as f:
        csv = f.read()

    for i in range (0,50):
        result += csv
        if Runner.run_process(result):
            return result

