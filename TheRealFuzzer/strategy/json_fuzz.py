import json
import base64
import random
from . import bad_stuff

class JSON_Fuzzer():
    def __init__(self, Runner, content, reporter):
        self.runner = Runner
        self.content = content
        self.reporter = reporter

        self.reporter.set_fuzzer('JSON Fuzzer')

    def strategies(self):
        return [
            # self.expand_file(),
            # self.negate_input(),
            # self.do_bad_to_value(),
            # self.expand_file_bad(),
        ]

    # Simple strategy - expand file size from empty
    def expand_file(self):
        self.reporter.set_strategy('expand_file')

        payload = ''
        # Empty file
        run = self.runner.run_process(payload)
        if run:
            if run[0]:
                return payload

        for i in range (0,30):
            payload += str(self.content)
            run = self.runner.run_process(payload)
            if run: 
                if run[0]:
                    return payload

    # Negates both the key and input value
    # NOTE May not be good strategy as a program coverage will likely increase if we fuzz the 
    #      value rather than the key
    def negate_input(self):
        self.reporter.set_strategy('negate_input')

        payload = {}
        new_value = ''

        for key in self.content:
            if isinstance(self.content[key], int):
                new_value = -self.content[key]
            else:
                new_value = bytearray(str(self.content[key]), 'utf-8')
                new_value = ''.join([chr(item ^ 255) for item in new_value])
    
            payload[key] = new_value

        payload = json.dumps(payload)
        run = self.runner.run_process(payload)

        if run:
            return payload


    # Accounts for overflow by adding 'bad' values 
    def do_bad_to_value(self):
        self.reporter.set_strategy('do_bad_to_value')


        def process_func(Runner, content):
            bad_ints = bad_stuff.bad_integers()
            bad_str =  bad_stuff.bad_strings()

            for key in content:
                if isinstance(content[key], int):
                    loc = random.randint(0, len(bad_ints) - 1)
                    content[key] = bad_ints[loc]

                else:
                    loc = random.randint(0, len(bad_str) - 1)
                    content[key] = bad_str[loc]

            return content

        for i in range(0, 20):
            payload = process_func(self.runner, self.content)

            payload = json.dumps(payload)
            if self.runner.run_process(payload):
                return payload

    # expand the file while creating 'bad' key-value pairs
    def expand_file_bad(self):
        self.reporter.set_strategy('expand_file_bad')

        bad_ints = bad_stuff.bad_integers()
        bad_str =  bad_stuff.bad_strings()

        combine = bad_ints + bad_str
        
        for i in range(0, 20):

            loc_key = random.randint(0, len(bad_str) - 1)
            loc_value = random.randint(0, len(combine) - 1)

            self.content[bad_str[loc_key]] = combine[loc_value]

        payload = json.dumps(self.content)
        if self.runner.run_process(payload):
            return payload