import random
from .bad_stuff import magic_numbers

# https://h0mbre.github.io/Fuzzing-Like-A-Caveman/
class JPG_Fuzzer():
    def __init__(self, Runner, input, reporter):
        self.runner = Runner
        self.input = input
        self.reporter = reporter

        self.reporter.set_fuzzer('JPG Fuzzer')

    def strategies(self):
        return [
            self.increment(),
            self.decrement(),
            self.bit_flip(),
            self.byte_flip(),
            self.overwrite_byte_sequences(),
            self.expand_file(),
        ]
            

    def increment(self):
        self.reporter.set_strategy('increment')
        
        for j in range(0, 200):
            payload = self.input

            num_to_increment = int((len(payload) - 4) * 0.01)
            indices_to_increment = range(4, (len(payload) - 4)) # accounts for SOI and EOI

            chosen_indexes = []

            for i in range(0, num_to_increment):
                loc = random.choice(indices_to_increment)
                payload[loc] = (payload[loc] % 255) + 1
                
            if self.runner.run_process(payload):
                return payload

    def decrement(self):
        self.reporter.set_strategy('decrement')
        
        for j in range(0, 200):
            payload = self.input

            num_to_decrement = int((len(payload) - 4) * 0.01)
            indices_to_decrement = range(4, (len(payload) - 4)) # accounts for SOI and EOI

            chosen_indexes = []

            for i in range(0, num_to_decrement):
                loc = random.choice(indices_to_decrement)
                payload[loc] = (payload[loc] - 1) % 255
                
            if self.runner.run_process(payload):
                return payload

    def bit_flip(self):
        self.reporter.set_strategy('bit_flip')
        
        for j in range(0, 200):
            payload = self.input


            num_of_flips = int((len(payload) - 4) * 0.005)
            indices_to_flip = range(4, (len(payload) - 4)) # accounts for SOI and EOI

            chosen_indexes = []

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

            
            if self.runner.run_process(payload):
                return payload


    def byte_flip(self):
        self.reporter.set_strategy('byte_flip')
        
        for j in range(0, 200):
            payload = self.input


            num_of_flips = int((len(payload) - 4) * 0.01)
            indices_to_flip = range(4, (len(payload) - 4)) # accounts for SOI and EOI

            chosen_indexes = []

            for i in range(0, num_of_flips):
                loc =random.choice(indices_to_flip)
                payload[loc] = payload[loc] ^ 0xff
                
            if self.runner.run_process(payload):
                return payload

    def overwrite_byte_sequences(self):
        self.reporter.set_strategy('overwrite_byte_sequences')

        for i in range(0, 200):

            payload = self.input

            picked_magic = magic_numbers()[random.choice([0,1,2])] #random.choice(magic_numbers())
            
            index = range(4, len(payload) - 4)
            picked_index = random.choice(index)

            if picked_magic[0] == 1:

                if picked_magic[1] == 255:			# 0xFF
                    payload[picked_index] = 255
                elif picked_magic[1] == 127:			# 0x7F
                    payload[picked_index] = 127
                elif picked_magic[1] == 0:			# 0x00
                    payload[picked_index] = 0


        # here we are hardcoding all the byte overwrites for all of the tuples that begin (2, )
            elif picked_magic[0] == 2:
                if picked_magic[1] == 255:			# 0xFFFF
                    payload[picked_index] = 255
                    payload[picked_index + 1] = 255
                elif picked_magic[1] == 0:			# 0x0000
                    payload[picked_index] = 0
                    payload[picked_index + 1] = 0

            # here we are hardcoding all of the byte overwrites for all of the tuples that being (4, )
            elif picked_magic[0] == 4:
                if picked_magic[1] == 255:			# 0xFFFFFFFF
                    payload[picked_index] = 255
                    payload[picked_index + 1] = 255
                    payload[picked_index + 2] = 255
                    payload[picked_index + 3] = 255
                elif picked_magic[1] == 0:			# 0x00000000
                    payload[picked_index] = 0
                    payload[picked_index + 1] = 0
                    payload[picked_index + 2] = 0
                    payload[picked_index + 3] = 0
                elif picked_magic[1] == 128:			# 0x80000000
                    payload[picked_index] = 128
                    payload[picked_index + 1] = 0
                    payload[picked_index + 2] = 0
                    payload[picked_index + 3] = 0
                elif picked_magic[1] == 64:			# 0x40000000
                    payload[picked_index] = 64
                    payload[picked_index + 1] = 0
                    payload[picked_index + 2] = 0
                    payload[picked_index + 3] = 0
                elif picked_magic[1] == 127:			# 0x7FFFFFFF
                    payload[picked_index] = 127
                    payload[picked_index + 1] = 255
                    payload[picked_index + 2] = 255
                    payload[picked_index + 3] = 255

            if self.runner.run_process(payload):
                return payload

    def expand_file(self):
        self.reporter.set_strategy('expand_file')

        content = self.input
        get_SOI = content[:4]
        get_EOI = content[-4:]
        get_body = content[4:-4]

        for i in range(1, 3000, 300):
            payload = get_SOI
            payload += get_body*i
            payload += get_EOI

            if self.runner.run_process(payload):
                return payload
