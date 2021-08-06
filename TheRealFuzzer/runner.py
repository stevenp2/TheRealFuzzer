import subprocess
import os, signal
import re
import xml
import xml.etree.ElementTree as ET
# import multiprocessing as MP


class Runner:
    def __init__(self):
        self.set_return_codes()
            
    # Returns True if there is an segmentation fault
    def run_process(self, payload):        
        if type(payload) is str:
            payload = payload.encode()

        process_as = [f'qemu-{self.arch}', f'{self.binary}'] if self.arch else self.binary
        p = subprocess.Popen(process_as, 
                                stdin  = subprocess.PIPE, 
                                stdout = subprocess.DEVNULL,
                                stderr = subprocess.DEVNULL)

        p.communicate(payload)

        self.reporter.counter += 1

        return self.process_return_code(p, payload)

    def run_process_coverage(self, payload):
        if type(payload) is str:
            payload = payload.encode()

        if type(payload) is xml.etree.ElementTree.Element:
            payload = ET.tostring(payload)

        process_as = [f'qemu-{self.arch}', '-d', 'exec,nochain' ,'-D', '../tmp/program_exec', f'{self.binary}'] if self.arch else self.binary
        p = subprocess.Popen(process_as, 
                                stdin  = subprocess.PIPE, 
                                stdout = subprocess.DEVNULL,
                                stderr = subprocess.DEVNULL)

        p.communicate(payload)

        self.reporter.counter += 1

        self.process_trace_file()


        return self.process_return_code(p, payload)

    # detects the type of crash
    def process_return_code(self, p, payload):
        if p.returncode == 0:
            self.return_codes['0'] += 1
        elif p.returncode == 1:
            self.return_codes['1'] += 1
        elif p.returncode == -6:
            self.return_codes['-6'] += 1
        elif p.returncode == -11:
            self.return_codes['-11'] += 1
            self.reporter.bad_found()

            return (True, payload)


    def initial_process_coverage(self):
        os.system(f"qemu-{self.arch} -d exec,nochain -D ../tmp/program_exec {self.binary} < {self.input_file} >/dev/null 2>&1")
        # subprocess.run([f'qemu-{self.arch}', '-d', 'exec,nochain', '-D', '../tmp/program_exec', f'{self.binary}', '<', f'{self.input_file}'])
        self.process_trace_file()

    def process_trace_file(self):
        with open('../tmp/program_exec') as f:
            for line in f.readlines():
                function = re.search(r"\s*([\S]+)$", line)
                if function != None:
                    function = function[0]
                    address = re.search(r"/(.*)/", line)[1]
                    
                    if function not in self.coverage_func:
                        self.coverage_func.append(function)


                    address_list = self.coverage_func_addr.get(function, address)
                    if address_list == address:
                        self.coverage_func_addr[function] = [address_list]

                    else:
                        if address not in address_list:
                            address_list.append(address)


    def set_binary(self, binary_file):
        self.binary = binary_file
    
    def set_input_file(self, input_file):
        self.input_file = input_file

    def set_arch(self, arch):
        self.arch = arch

    def set_reporter(self, reporter):
        self.reporter = reporter

    def set_coverage(self):
        self.coverage_func_addr = {}
        self.coverage_func = []

    def set_return_codes(self):
        self.return_codes = {'0':0, '1':0, '-6':0, '-11':0}