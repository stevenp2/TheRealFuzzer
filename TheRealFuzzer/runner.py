import subprocess
import os, signal
import re
# import multiprocessing as MP


class Runner:
    def __init__(self):
        pass
            
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
                                                #in_asm,nochain
        # NOTE -d in_asm doesn not trace for each executed instruction --> traces which instructions are translated
        #      -d cpu, or -d exec with nochain is what we want to use
        process_as = [f'qemu-{self.arch}', '-d', 'exec,nochain' ,'-D', '../tmp/program_exec', f'{self.binary}'] if self.arch else self.binary
        p = subprocess.Popen(process_as, 
                                stdin  = subprocess.PIPE, 
                                stdout = subprocess.DEVNULL,
                                stderr = subprocess.DEVNULL)

        p.communicate(payload)

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
                

        return self.process_return_code(p, payload)


    def process_return_code(self, p, payload):
        if p.returncode == -11:
            # Accounts for empty payload being returned
            # NOTE may be better to create bad.txt file here

            self.reporter.bad_found()

            return (True, payload)
        
        # if p.returncode == 1:
        #     print(f'likely error with arguments - will exit program now')
        #     exit(0)



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