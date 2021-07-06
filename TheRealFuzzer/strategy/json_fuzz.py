import json
import base64

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
        # # print(key)
        # if isinstance(key, int):
        #     new_key = -key
        # else:
        #     new_key = bytearray(key, 'utf-8')
        #     new_key = ''.join([chr(item ^ 255) for item in new_key])

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
