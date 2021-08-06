import os

class Reporter:
    def __init__(self):
        self.counter = 0
    
    def send_to_stdout(self, message):
        print(message)

    def write(self, message):
        self.f.write(f'\n{message}\n')
    
    def bad_found(self):
        self.f.write(f'Bad found in iteration number {self.counter}\n')

    def set_file(self, f):
        self.f = f

    def set_fuzzer(self, fuzzer):
        self.f.write(f'Fuzzing using: {fuzzer}\n')
        self.f.flush()

    def set_strategy(self, strategy):
        self.f.write(f'\nStrategy: {strategy}\n')
        self.f.flush()
        self.counter = 0

