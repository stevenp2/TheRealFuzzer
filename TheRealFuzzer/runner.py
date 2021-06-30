import subprocess

from checker import * 
from pwn import *
from strategy import csv_fuzz


file_types = ['csv', 'elf', 'jpeg', 'json', 'pdf', 'txt'] # txt is deafult

class Runner:
    def __init__(self):
        pass

    def run_process(self):
        with process(self.binary) as p:
            payload = ''

            if self.type == 'csv':
                content, delimiter = csv_fuzz.read_csv_input(self.input_file)
                
                # Given content and delimiter, implement strategy
                payload += csv_fuzz.eliminate_delimiters(content)

            p.send(payload)        

            # TODO: Find out way to get system response at the end of the program
            return p.proc.stderr


    def set_binary(self, binary_file):
        self.binary = binary_file
    
    def set_input_file(self, input_file):
        self.input_file = input_file

    def set_type(self, file_type):
        self.type = file_type