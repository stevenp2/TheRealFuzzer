import csv
import random
import re
from .bad_stuff import bad_integers

class Csv_Fuzzer():
    def __init__(self, Runner, content):
        self.runner = Runner
        self.content = content

    def strategies(self):
        return [
            self.negate_everything(),
            self.vary_delimiters(),
            self.expand_file(),
            self.oob_ints(),
            self.bit_flip(),
        ]

    def strategies_txt(self):
        return [
            self.expand_file(),
            self.oob_ints(),
            self.negate_everything(),
            self.bit_flip(),
        ]

    # Simple strategy - have fun with delimiters
    def vary_delimiters(self):
        self.content, delimiter = self._read_csv_input()

        if delimiter == None:
            return

        try_delimiters = ['|', 'a', '', '@', '🐒', 'word', '水', '水水水']

        for d in try_delimiters:
            payload = self.content.replace(delimiter, d)
            if self.runner.run_process(payload):
                return payload
            
    # Simple strategy - expand file size from empty
    def expand_file(self):
        payload = ''

        # Empty file
        run = self.runner.run_process(payload)
        if run:
            if run[0]:
                return payload

        for i in range (0,50):
            payload += self.content
            run = self.runner.run_process(payload)
            if run: 
                if run[0]:
                    return payload

    # Simple strategy - expand file size from empty
    def negate_everything(self):
        c = csv.reader(self.content)
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

        if self.runner.run_process(payload_csv):
            return payload_csv

    def oob_ints(self):
        # regex
        integers = re.findall(r'[0-9]+', self.content)

        def process_func(Runner, content, possible_int):

            for integer in integers:
                content = content.replace(integer, str(possible_int))

            return content

        for bad_int in bad_integers():
            payload = process_func(self.runner, self.content, bad_int)
            if self.runner.run_process(payload):
                return payload

    # randomly flips some bits in string
    def bit_flip(self):

        for j in range(0, 300):

            byte_str = bytearray(self.content, 'utf-8')

            for i in range(0, len(byte_str)):
                if random.randint(0, 2) == 1:
                    byte_str[i] ^= random.getrandbits(7)


            payload = byte_str.decode('ascii')

            if self.runner.run_process(payload):
                return payload

     # NOTE: content is in the form  [[word1, word2, 3], [nextline, abd, so], [forth, 1, 1]]
    def _read_csv_input(self):
        try:
            sniffer = csv.Sniffer()
            csv_file = sniffer.sniff(self.content)
            delimiter = csv_file.delimiter
            return self.content, delimiter 
            
        except:
            return self.content, None
        