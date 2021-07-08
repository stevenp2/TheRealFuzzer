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
        # TODO: get rid of all the ugly if statements and fat lines of code

        file_type = check_type(input_file)

        if file_type == 'json':
            with open(input_file, 'r') as f:
                content = json.load(f)
                
                # expand file as plaintext
                bad_input = json_strategy.expand_file(self.runner, content)
                
                if bad_input == None:
                    # negate numbers
                    bad_input = json_strategy.negate_input(self.runner, content)

                if bad_input == None:
                    # fill value with bad integers
                    bad_input = json_strategy.do_bad_to_value(self.runner, content)

                if bad_input == None:
                    # append bad values into the json data
                    bad_input = json_strategy.expand_file_bad(self.runner, content)

        elif file_type == 'xml':
            with open(input_file, 'r') as f: 
                tree = ET.parse(f)

            # to not have the state of the original xml file adjusted
            root = deepcopy(tree.getroot())

             # increase size of xml file by increasing the number of sub tags
            bad_input = xml_strategy.add_tags(self.runner, root, 40)

            if bad_input == None:
                # add %p, %s, %x, etc. into elements
                bad_input = xml_strategy.edit_elements_format_str(self.runner, root)

            if bad_input == None:
                # send large amount of empty tags
                bad_input = xml_strategy.bombard_tag(self.runner, root)

            if bad_input == None:
                # increase size of elements for possible overflow
                bad_input = xml_strategy.edit_elements_overflow(self.runner, root)

            if bad_input == None:
                # append a randomly selected elements inside headers
                bad_input = xml_strategy.shuffle_elements(self.runner, root)


        # NOTE sometimes csv failes to detect whether a plaintext is csv or not
        elif file_type == 'csv':

            with open(input_file, 'r') as f:
                content = f.read()
            
            bad_input = csv_strategy.negate_everything(self.runner, content)

            # remove delimiters
            if bad_input == None:
                bad_input = csv_strategy.vary_delimiters(self.runner, content)
            
            # expand file strategy --> WORKS
            if bad_input == None:
                bad_input = csv_strategy.expand_file(self.runner, content)

            # replace ints with possible oob ints:
            if bad_input == None:
                bad_input = csv_strategy.oob_ints(self.runner, content)

            # flip some bits
            if bad_input == None:
                bad_input = csv_strategy.bit_flip(self.runner, content)


        elif file_type == 'txt':
            # apply some same strategies from csv
            with open(input_file, 'r') as f:
                content = f.read()

            bad_input = csv_strategy.expand_file(self.runner, content)

            if bad_input == None:
                bad_input = csv_strategy.oob_ints(self.runner, content)

            if bad_input == None:
                bad_input = csv_strategy.negate_everything(self.runner, content)

            if bad_input == None:
                bad_input = csv_strategy.bit_flip(self.runner, content)

        # NOTE for the case of pdf and jpg where f.read() cannot decode
        else:
            pass

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



