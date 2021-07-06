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
        if check_type(input_file) == 'json':
            with open(input_file, 'r') as f:
                content = json.load(f)
                
                # expand file as plaintext
                bad_input = json_strategy.expand_file(self.runner, content)
                
                if bad_input == None:
                    # negate numbers
                    bad_input = json_strategy.negate_input(self.runner, content)


        elif check_type(input_file) == 'xml':
            with open(input_file, 'r') as f: 
                tree = ET.parse(f)
                root = tree.getroot()

            # print(f'{root.tag} and {root.attrib}')
            
            for child in root:
                print(child.tag, child.attrib)
                if child.attrib != {}:
                    
                    for baby in child:
                        print(baby.tag, baby.attrib)

            # print(ET.tostring(root, encoding='utf8').decode('utf8'))    # <--- adds in an unwanted <?xml version='1.0' encoding='utf8'?>



        elif check_type(input_file) == 'csv':
            content, delimiter = csv_strategy.read_csv_input(input_file)

            # remove delimiters
            bad_input = csv_strategy.vary_delimiters(self.runner, content, delimiter)
            
            # expand file strategy --> WORKS
            if bad_input == None:
                bad_input = csv_strategy.expand_file(self.runner, content, delimiter)

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



