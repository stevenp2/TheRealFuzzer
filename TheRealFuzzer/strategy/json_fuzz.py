import json
import base64
import random
from . import bad_stuff
# Simple strategy - expand file size from empty
def expand_file(Runner, content):
    payload = ''

    # Empty file
    run = Runner.run_process(payload)
    if run:
        if run[0]:
            return payload

    for i in range (0,30):
        payload += str(content)
        run = Runner.run_process(payload)
        if run: 
            if run[0]:
                return payload

# Negates both the key and input value
# NOTE May not be good strategy as a program coverage will likely increase if we fuzz the 
#      value rather than the key
def negate_input(Runner, content):
    payload = {}
    new_value = ''

    for key in content:
        if isinstance(content[key], int):
            new_value = -content[key]
        else:
            new_value = bytearray(str(content[key]), 'utf-8')
            new_value = ''.join([chr(item ^ 255) for item in new_value])
  
        payload[key] = new_value

    payload = json.dumps(payload)
    run = Runner.run_process(payload)

    if run:
        return payload


# Accounts for overflow as well
def do_bad_to_value(Runner, content):

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
        payload = process_func(Runner, content)

        payload = json.dumps(payload)
        if Runner.run_process(payload):
            return payload

def expand_file_bad(Runner, content):

    bad_ints = bad_stuff.bad_integers()
    bad_str =  bad_stuff.bad_strings()

    combine = bad_ints + bad_str
    
    for i in range(0, 20):

        loc_key = random.randint(0, len(bad_str) - 1)
        loc_value = random.randint(0, len(combine) - 1)

        content[bad_str[loc_key]] = combine[loc_value]

    payload = json.dumps(content)
    if Runner.run_process(payload):
        return payload