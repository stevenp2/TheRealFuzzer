#!/usr/bin/python3

import sys
import os
import logging
import argparse
import json
import xml.etree.ElementTree as ET

import runner as r
from strategy.csv_fuzz import CSV_Fuzzer
from strategy.json_fuzz import JSON_Fuzzer
from strategy.xml_fuzz import XML_Fuzzer
from strategy.txt_fuzz import TXT_Fuzzzer

from copy import deepcopy
from checker import check_type, check_arch


class Fuzzer():
    def __init__(self, binary, input_file, Runner):
        self.binary = binary
        self.input_file = input_file
        self.runner = Runner

    def run(self):
        self.runner.set_binary(binary)
        self.runner.set_input_file(input_file)
        self.runner.set_arch(check_arch(binary))

        file_type = check_type(input_file)
        outputs = []

        with open(input_file, 'r') as f:

            if file_type == 'json':
                content = json.load(f)  
                outputs += JSON_Fuzzer(self.runner, content).strategies()

            elif file_type == 'xml':
                tree = ET.parse(f)
                # to not have the state of the original xml file adjusted
                content = deepcopy(tree.getroot())
                outputs += XML_Fuzzer(self.runner, content).strategies()

            elif file_type == 'csv':
                content = f.read()
                outputs += CSV_Fuzzer(self.runner, content).strategies()

            elif file_type == 'txt':
                content = f.read()
                outputs += TXT_Fuzzzer(self.runner, content).strategies()

            # NOTE for the case of pdf and jpg where f.read() cannot decode
            else:
                pass

        outputs = list(filter(None, outputs))
        bad_input = outputs[0] if outputs else None

        # Fall back if cannot fuzz using stage-1 fuzzing --> mutation based fuzzing

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



