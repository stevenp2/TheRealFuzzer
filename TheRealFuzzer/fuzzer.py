#!/usr/bin/python3

import sys
import os
import logging
import argparse

import runner as r
from strategy.csv_fuzz import *
from checker import check_type

class Fuzzer():
    def __init__(self, binary, input_file, Runner):
        self.binary = binary
        self.input_file = input_file
        self.runner = Runner

    def run(self):
        self.runner.set_binary(binary)
        # self.runner.set_input_file(input_file)

        bad_input = ''

        if check_type(input_file) == 'csv':
            content, delimiter = read_csv_input(input_file)
            # remove delimiters
            bad_input = vary_delimiters(self.runner, content, delimiter)
            # expand file strategy --> WORKS
            bad_input = expand_file(self.runner, content, delimiter)
            
        return bad_input



def main(binary, input_file):
    
    runner = r.Runner()
    fuzzer = Fuzzer(binary, input_file, runner)


    payload = fuzzer.run()

    if payload != None:
        with open('./bad.txt', 'w') as f:
            f.write(payload)


if __name__ == "__main__":

    test_path = "../testfiles/"

    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} [binary] [input_file]")
        exit(0)

    binary = test_path + sys.argv[1]   #NOTE: change to binary = sys.argv[1]
    input_file = test_path + sys.argv[2] #NOTE: change to input_file = sys.argv[2]

    if not (os.path.isfile(binary)):
        sys.exit("binary does not exist")

    if not (os.path.isfile(binary)):
        sys.exit("input_file does not exist")

    main(binary, input_file)



