import csv
import random

# NOTE: content is in the form  [[word1, word2, 3], [nextline, abd, so], [forth, 1, 1]]
def read_csv_input(text):
    sniffer = csv.Sniffer()
    content = []
    delimiter = ',' # by default
 
    with open(text) as f:
        csv_file = sniffer.sniff(f.read(1024))
        delimiter = csv_file.delimiter

        f.seek(0)
        reader = csv.reader(f, delimiter=delimiter)

        for row in reader:
            content.append(row)

    return content, delimiter 
    
# Simple strategy #1
def eliminate_delimiters(content):
    result = ''
    for i in range(0, len(content)):
        result += ''.join(content[i]) + '\n'

    return result

