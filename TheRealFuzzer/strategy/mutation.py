import random
import csv
import json
import xml.etree.ElementTree as ET
from copy import deepcopy
import re
import os

import matplotlib.pyplot as plt
from . import bad_stuff


class Mutation_Fuzzer():
    def __init__(self, Runner, f, reporter, file_type):
        self.runner = Runner
        self.reporter = reporter
        self.file_type = file_type
        self.f = f

        self.reporter.set_fuzzer('Mutation Fuzzer')

        self.payloads = []

        self.exec_blacklist = []
        self.loop_counter = [0, 0] # [exec, number of repetitions]

    def initiate(self):
        self.reporter.send_to_stdout('Initiating coverage fuzzing')

        self.payload = self.determine_content(self.f)
        self.payloads.append(self.payload)

        self.runner.set_coverage()
        
        # generate coverage from initial input file
        self.runner.initial_process_coverage()

        # plotting initial coverage
        plt.figure(1)
        plt.bar(self.runner.coverage_func, self.calculate_coverage(), color='r', label='input file')
        plt.xticks(rotation = 90)
        plt.ylabel('diff addresses')
        plt.legend(loc='best')

        self.perform_coverage_fuzz(self.file_type)

        # plotting coverage after payload has been found
        plt.bar(self.runner.coverage_func, self.calculate_coverage(), color='greenyellow', alpha=0.3, label='coverage')
        plt.legend(loc='best')
        plt.savefig('log_report/function_coverage.png', bbox_inches="tight")

        # plotting the return codes
        return_codes = self.runner.return_codes
        plt.figure(2)
        plt.bar(range(len(return_codes)), list(return_codes.values()), align='center')
        plt.xticks(range(len(return_codes)), list(return_codes.keys()))
        plt.xlabel('return codes')
        plt.ylabel('amount')
        plt.savefig('log_report/return_code.png', bbox_inches="tight")

        return self.payload

    def perform_coverage_fuzz(self, file_type):
        bad_str =  bad_stuff.bad_strings()
        bad_ints = bad_stuff.bad_integers()
        magic_numbers = bad_stuff.bad_integers()

        while self.payloads != []:
            total = self.total_addr() # total of previous
            
            if self.determine_loop(total):
                self.reporter.send_to_stdout('Dead end detected, resetting')
                total = self.reset(total)

            if self.file_type == 'json':
                payload = self.json_mutation(bad_ints, bad_str, self.payloads[len(self.payloads) - 1])
            elif self.file_type == 'xml':
                payload = self.xml_mutation(bad_ints, bad_str, self.payloads[len(self.payloads) - 1])
            elif self.file_type == 'csv':
                payload = self.csv_mutatation(bad_str, self.payloads[len(self.payloads) - 1])
            elif self.file_type == 'txt':
                payload = self.txt_mutation(bad_str, self.payloads[len(self.payloads) - 1])
            elif self.file_type == 'jpeg':
                # payload = self.csv_mutatation(bad_str, self.payloads[len(self.payloads) - 1])
                pass

            result = self.runner.run_process_coverage(payload)

            if result != None:
                self.payload = payload
                self.reporter.send_to_stdout('Found Payload')
                break

            new_total = self.total_addr()

            if (new_total > total):
                if new_total not in self.exec_blacklist:

                    # set new payload
                    self.payload = payload
                    self.reporter.send_to_stdout(f'\rNew path discovered with {new_total} different addresses - adjusting payload')

                    self.loop_counter[0] = new_total
                    self.loop_counter[1] = 0

                    self.payloads.append(self.payload)

            else:
                self.loop_counter[1] += 1
        
    def reset(self, total):
        self.loop_counter[0] = 0
        self.loop_counter[1] = 0

        self.exec_blacklist.append(total)
        self.runner.set_coverage()
        self.payload = self.payloads[0]

        for i in range(0, len(self.payloads) -1):
            self.payloads.pop()

        return 0

    def determine_loop(self, total):

        if self.loop_counter[1] == int(16.498): # average derived from repeating mutations for all fuzzers
            return True
        
        return False


    def calculate_coverage(self):
        func_cover = []
        for function in self.runner.coverage_func:
            addresss_list = self.runner.coverage_func_addr[function]
            func_cover.append(len(addresss_list))
            # print(f'{function}: {len(addresss_list)}')

        return func_cover

    def total_addr(self):
        total_addr = 0
        for function in self.runner.coverage_func:
            total_addr += len(self.runner.coverage_func_addr[function])

        return total_addr


    def csv_mutatation(self, bad_str, content):

        random_index = random.choice(range(0, len(content)))
        random_replacement = random.choice(range(0, len(bad_str)))

        payload = content.replace(content[random_index], bad_str[random_replacement])

        return payload

        

    def json_mutation(self, bad_ints, bad_str, content):
        
        for key in content:
            if isinstance(content[key], int):
                loc = random.randint(0, len(bad_ints) - 1)
                content[key] = bad_ints[loc]

            else:
                loc = random.randint(0, len(bad_str) - 1)
                content[key] = bad_str[loc]

        content = json.dumps(content)

        return content

    def xml_mutation(self, bad_ints, bad_str, root):

        for child in root.iter():
            if child.attrib:
                for attrib in child.attrib:
                    attr_string = child.attrib[attrib]
                    child.attrib[attrib] = self._xml_do_bad(attr_string, bad_ints, bad_str)

            if child.text:
                empty_text = re.search('\\n +', child.text)

                if not empty_text:
                    text_string = child.text
                    child.text = self._xml_do_bad(text_string, bad_ints, bad_str)

        # payload = ET.tostring(root)
        
        return root

    def _xml_do_bad(self, string, bad_ints, bad_str):
        str_len = len(string)

        int_or_str = random.choice([0, 1])
        random_loc = random.choice(range(0, len(string)))

        if type(int_or_str) is int:
            string = string.replace(string[random_loc], str(bad_ints[random.choice(range(0, len(bad_ints)))]))
        else:
            string = string.replace(string[random_loc], bad_ints[random.choice(range(0, len(bad_str)))])   

        return string

    def txt_mutation(self, bad_str, content):

        random_index = random.choice(range(0, len(content)))
        random_replacement = random.choice(range(0, len(bad_str)))

        payload = content.replace(content[random_index], bad_str[random_replacement])
        
        return payload

    def jpg_mutation(self, input):
        
        payload = input

        num_of_flips = int((len(payload) - 4) * 0.005)
        indices_to_flip = range(4, (len(payload) - 4)) # accounts for SOI and EOI

        for i in range(0, num_of_flips):
            loc = random.choice(indices_to_flip)

            binary = list(bin(payload[loc])[2:])
            index = random.choice(range(0,8))

            while len(binary) < 8:
                binary.append('0')

            if binary[index] == '0':
                binary[index] = '1'
            elif binary[index] == '1':
                binary[index] = '0'

            combine_binary = ''.join(binary)

            integer = int(combine_binary, 2)

            payload[loc] = payload[loc]

            
        return payload


    def determine_content(self, f):
        if self.file_type == 'json':
            return json.load(f)
 
        elif self.file_type == 'xml':
            return ET.parse(f).getroot()

        elif self.file_type == 'csv':
            return f.read()

        elif self.file_type == 'txt':
            return f.read()
            
        elif self.file_type == 'jpeg':
            return bytearray(f.read())
