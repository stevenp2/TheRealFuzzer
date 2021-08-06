#!/usr/bin/python3

import sys
import os
import logging
import argparse
import json
import xml.etree.ElementTree as ET
import exifread
import matplotlib.pyplot as plt

import runner as r
from reporter import Reporter
from strategy.csv_fuzz import CSV_Fuzzer
from strategy.json_fuzz import JSON_Fuzzer
from strategy.xml_fuzz import XML_Fuzzer
from strategy.txt_fuzz import TXT_Fuzzzer
from strategy.jpg_fuzz import JPG_Fuzzer
from strategy.mutation import Mutation_Fuzzer

from copy import deepcopy
from checker import check_type, check_arch


class Fuzzer():
    def __init__(self, binary, input_file, Runner):
        self.binary = binary
        self.input_file = input_file
        self.runner = Runner

    def run(self):
        file_type = check_type(input_file)
        outputs = []

        reporter = Reporter()
        directory = os.path.dirname("log_report/")

        if not os.path.exists(directory):
            os.makedirs(directory)

        fp = open(directory + '/log', 'w')
        reporter.set_file(fp)

        self.runner.set_binary(binary)
        self.runner.set_input_file(input_file)
        self.runner.set_arch(check_arch(binary))
        self.runner.set_reporter(reporter)


        if file_type == 'json':
            with open(input_file, 'r') as f:
                content = json.load(f)  
                f.close()
                outputs += JSON_Fuzzer(self.runner, content, reporter).strategies()

        elif file_type == 'xml':
            with open(input_file, 'r') as f:
                tree = ET.parse(f)
                # to not have the state of the original xml file adjusted
                content = deepcopy(tree.getroot())
                f.close()
                outputs += XML_Fuzzer(self.runner, content, reporter).strategies()

        elif file_type == 'csv':
            with open(input_file, 'r') as f:
                content = f.read()
                f.close()
                outputs += CSV_Fuzzer(self.runner, content, reporter).strategies()

        elif file_type == 'txt':
            with open(input_file, 'r') as f:
                content = f.read()
                f.close()
                outputs += TXT_Fuzzzer(self.runner, content, reporter).strategies()

        elif file_type == 'jpeg':
            with open(input_file, 'rb') as f:
                content = bytearray(f.read())
                f.close()
                outputs += JPG_Fuzzer(self.runner, content, reporter).strategies()

        outputs = list(filter(None, outputs))
        bad_input = outputs[0] if outputs else None

        if bad_input:
            return_codes = self.runner.return_codes
            plt.bar(range(len(return_codes)), list(return_codes.values()), align='center')
            plt.xticks(range(len(return_codes)), list(return_codes.keys()))
            plt.xlabel('return codes')
            plt.ylabel('amount')
            plt.savefig('log_report/return_code.png', bbox_inches="tight")

            if isinstance(bad_input, bytes):
                return bad_input
            else:
                return bad_input.encode('utf-8')

        # Fall back if cannot fuzz using basic techniques --> mutation based fuzzing
        else:
            bad_input = None
            directory = os.path.dirname("../tmp/")

            if not os.path.exists(directory):
                os.makedirs(directory)

            if file_type == 'jpeg':
                with open(input_file, 'rb') as f:
                    mutation = Mutation_Fuzzer(self.runner, f, reporter, file_type)
                    bad_input = mutation.initiate()

            else:
                with open(input_file, 'r') as f:
                    mutation = Mutation_Fuzzer(self.runner, f, reporter, file_type)
                    bad_input = mutation.initiate()

            if bad_input:
                if isinstance(bad_input, bytes):
                    return bad_input
                else:
                    return bad_input.encode('utf-8')

        fp.close()


def main(binary, input_file):
    runner = r.Runner()
    fuzzer = Fuzzer(binary, input_file, runner)


    payload = fuzzer.run()
    if payload != None:
        with open('./bad.txt', 'wb') as f:
            f.write(payload)


if __name__ == "__main__":

    test_path = '' # "../testfiles/"

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



