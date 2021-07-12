import subprocess
import os, signal
# import multiprocessing as MP


class Runner:
    def __init__(self):
        pass
            
    # Returns True if there is an segmentation fault
    def run_process(self, payload):
        # payload = self.craft_payload()
        

        if type(payload) is str:
            payload = payload.encode()

        # with subprocess.Popen(self.binary,
        #                       stdin=subprocess.PIPE,
        #                       stdout=subprocess.DEVNULL,
        #                       stderr=subprocess.DEVNULL) as p:

        #     payload = p.communicate(payload)

        p = subprocess.Popen([f'qemu-{self.arch}', '-d', 'strace', '-D', '../log_report/log', f'{self.binary}'], 
                                stdin = subprocess.PIPE, 
                                stdout = subprocess.DEVNULL,
                                stderr = subprocess.DEVNULL)
                                
        p.communicate(payload)

        if p.returncode == -11:
            # Accounts for empty payload being returned
            # NOTE may be better to create bad.txt file here

            return (True, payload)


    def set_binary(self, binary_file):
        self.binary = binary_file
    
    def set_input_file(self, input_file):
        self.input_file = input_file

    def set_arch(self, arch):
        self.arch = arch