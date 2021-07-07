#!/usr/bin/python3

import sys
import os
import logging
import argparse
import json
import xml.etree.ElementTree as ET

import runner as r
import strategy.csv_fuzz as csv_strategy
import strategy.json_fuzz as json_strategy
import strategy.xml_fuzz as xml_strategy

from copy import deepcopy
from checker import check_type

class Fuzzer():
    def __init__(self, binary, input_file, Runner):
        self.binary = binary
        self.input_file = input_file
        self.runner = Runner

    def run(self):
        self.runner.set_binary(binary)
        # self.runner.set_input_file(input_file)

        bad_input = None
        # TODO: if bad_input is populated then immediately return the result
        # TODO: abstract out function calls

        file_type = check_type(input_file)

        if file_type == 'json':
            with open(input_file, 'r') as f:
                content = json.load(f)
                
                # expand file as plaintext
                bad_input = json_strategy.expand_file(self.runner, content)
                
                if bad_input == None:
                    # negate numbers
                    bad_input = json_strategy.negate_input(self.runner, content)


        elif file_type == 'xml':
            with open(input_file, 'r') as f: 
                tree = ET.parse(f)

            # to not have the state of the original xml file adjusted
            root = deepcopy(tree.getroot())

            bad_input = xml_strategy.add_tags(self.runner, root, 20) # dumps at 35

            if bad_input == None:
                bad_input = xml_strategy.edit_elements(self.runner, root)
            if bad_input == None:
                bad_input = xml_strategy.bombard_tag(self.runner, root)
            if bad_input == None:
                bad_input = xml_strategy.shuffle_elements(self.runner, root)


        elif file_type == 'csv':
            content, delimiter = csv_strategy.read_csv_input(input_file)

            # remove delimiters
            bad_input = csv_strategy.vary_delimiters(self.runner, content, delimiter)
            
            # expand file strategy --> WORKS
            if bad_input == None:
                bad_input = csv_strategy.expand_file(self.runner, content, delimiter)


        if bad_input:
            if isinstance(bad_input, bytes):
                return bad_input
            else:
                return bad_input.encode('utf-8')



def main(binary, input_file):
    runner = r.Runner()
    fuzzer = Fuzzer(binary, input_file, runner)


    payload = fuzzer.run()
    if payload != None:
        with open('./bad.txt', 'wb') as f:
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



