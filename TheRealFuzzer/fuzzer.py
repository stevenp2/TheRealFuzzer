#!/usr/bin/python3

import sys
import os
import logging
import argparse
import json
import xml.etree.ElementTree as ET

import runner as r
from strategy.csv_fuzz import Csv_Fuzzer
from strategy.json_fuzz import Json_Fuzzer
# from strategy.xml_fuzz import XML_Fuzzer

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

        file_type = check_type(input_file)
        outputs = []

        with open(input_file, 'r') as f:

            if file_type == 'json':
                content = json.load(f)
                    
                json_fuzz = Json_Fuzzer(self.runner, content)
                outputs += json_fuzz.strategies()


            elif file_type == 'xml':
                tree = ET.parse(f)
                # to not have the state of the original xml file adjusted
                root = deepcopy(tree.getroot())

                # xml_fuzz = XML_Fuzzer(self.runner, root)

                # outputs += filter(None, xml_fuzz.strategies())

                # if outputs:
                #     bad_input = outputs[0]

                #  # increase size of xml file by increasing the number of sub tags
                # bad_input = xml_strategy.add_tags(self.runner, root, 100)

                # if bad_input == None:
                #     # add %p, %s, %x, etc. into elements
                #     bad_input = xml_strategy.edit_elements_format_str(self.runner, root)

                # if bad_input == None:
                #     # send large amount of empty tags
                #     bad_input = xml_strategy.bombard_tag(self.runner, root)

                # if bad_input == None:
                #     # increase size of elements for possible overflow
                #     bad_input = xml_strategy.edit_elements_overflow(self.runner, root)

                # if bad_input == None:
                #     # append a randomly selected elements inside headers
                #     bad_input = xml_strategy.shuffle_elements(self.runner, root)


            # NOTE sometimes csv failes to detect whether a plaintext is csv or not
            elif file_type == 'csv':
                content = f.read()
                
                csv_fuzz = Csv_Fuzzer(self.runner, content)
                outputs += csv_fuzz.strategies()

            elif file_type == 'txt':
                # apply some same strategies from csv
                content = f.read()
            
                csv_fuzz = Csv_Fuzzer(self.runner, content)
                outputs += csv_fuzz.strategies_txt()

            # NOTE for the case of pdf and jpg where f.read() cannot decode
            else:
                pass

        outputs = list(filter(None, outputs))
        bad_input = outputs[0] if outputs else None

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



