import random
import csv
import json
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
        self.payload = self.determine_content(self.f)
        self.payloads.append(self.payload)

        self.runner.set_coverage()
        
        # generate coverage from initial input file
        self.runner.run_process_coverage(self.payload)
        # total = self.total_addr()

        # print(self.runner.coverage_func_addr)
        # print(self.runner.coverage_func)

        self.perform_coverage_fuzz(self.file_type)


        # func_addr = self.calculate_coverage()
        # plt.plot(self.runner.coverage_func, func_addr)
        # plt.xticks(rotation = 90)
        # plt.ylabel('diff addresses')
        # plt.show()

        return self.payload

    def perform_coverage_fuzz(self, file_type):
        bad_str =  bad_stuff.bad_strings()
        bad_ints = bad_stuff.bad_integers()
        magic_numbers = bad_stuff.bad_integers()

        while self.payloads != []:
            total = self.total_addr() # total of previous
            
            if self.determine_loop(total):
                total = self.reset(total)

                print(f'popped and blacklist is {self.exec_blacklist} and payloads len is {len(self.payloads)}')

            if self.file_type == 'json':
                payload = self.json_mutation(bad_str, self.payloads[len(self.payloads) - 1])
            elif self.file_type == 'xml':
                payload = self.csv_mutatation(bad_ints, bad_str, self.payloads[len(self.payloads) - 1])
            elif self.file_type == 'csv':
                # payload = self.csv_mutatation(bad_str, self.payloads[len(self.payloads) - 1])
                pass
            elif self.file_type == 'txt':
                # payload = self.csv_mutatation(bad_str, self.payloads[len(self.payloads) - 1])
                pass
            elif self.file_type == 'jpeg':
                # payload = self.csv_mutatation(bad_str, self.payloads[len(self.payloads) - 1])
                pass


            result = self.runner.run_process_coverage(payload)

            new_total = self.total_addr()

            if (new_total > total):

                if new_total not in self.exec_blacklist:

                    # set new payload
                    self.payload = payload
                    print('new payload')

                    self.loop_counter[0] = new_total
                    self.loop_counter[1] = 0

                    print(f"loop counter: {self.loop_counter}")

                    self.payloads.append(self.payload)

            else:
                self.loop_counter[1] += 1

            print(new_total)

            if result != None:
                break
        
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
        # num_func = len(self.runner.coverage_func)

        if self.loop_counter[1] == 20: # TODO change
            return True
        
        return False


    def calculate_coverage(self):
        func_cover = []
        for function in self.runner.coverage_func:
            addresss_list = self.runner.coverage_func_addr[function]
            func_cover.append(len(addresss_list))
            print(f'{function}: {len(addresss_list)}')

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

        

    def json_mutation(bad_ints, bad_str, content):

        for key in content:
            if isinstance(content[key], int):
                loc = random.randint(0, len(bad_ints) - 1)
                content[key] = bad_ints[loc]

            else:
                loc = random.randint(0, len(bad_str) - 1)
                content[key] = bad_str[loc]

        content = json.dumps(content)
        print(content)

        # self.runner.run_process(payload)
        exit()
        return payload

    def xml_mutation():
        pass

    def txt_mutation():
        pass

    def jpg_mutation():
        pass

    def determine_content(self, f):
        if self.file_type == 'json':
            return json.load(f)  

        elif self.file_type == 'xml':
            tree = ET.parse(f)
            return deepcopy(tree.getroot())

        elif self.file_type == 'csv':
            return f.read()

        elif self.file_type == 'txt':
            return f.read()
            
        elif self.file_type == 'jpeg':
            return bytearray(f.read())
                