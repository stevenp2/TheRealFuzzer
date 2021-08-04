import subprocess
import os, signal
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

        return self.process_return_code(p, payload)

    def run_process_coverage(self, payload):
        if type(payload) is str:
            payload = payload.encode()
                                                #in_asm,nochain
        # NOTE -d in_asm doesn not trace for each executed instruction --> traces which instructions are translated
        #      -d cpu, or -d exec with nochain is what we want to use
        process_as = [f'qemu-{self.arch}', '-d', 'exec' ,'-D', '../log_report/log', f'{self.binary}'] if self.arch else self.binary
        p = subprocess.Popen(process_as, 
                                stdin  = subprocess.PIPE, 
                                stdout = subprocess.DEVNULL,
                                stderr = subprocess.DEVNULL)

        p.communicate(payload)

        return self.process_return_code(p, payload)


    def process_return_code(self, p, payload):
        # if p.returncode == 1:
        #     print(f'likely error with arguments - will exit program now')
        #     exit(0)
        print(p.returncode)
        if p.returncode == -11:
            # Accounts for empty payload being returned
            # NOTE may be better to create bad.txt file here

            return (True, payload)

    def initial_coverage(self, f):
        if type(f) is str:
            f = f.encode()

        process_as = [f'qemu-{self.arch}', '-d', 'exec' ,'-D', '../log_report/log', f'{self.binary}'] if self.arch else self.binary

        p = subprocess.Popen(process_as, 
                                stdin  = subprocess.PIPE, 
                                stdout = subprocess.DEVNULL,
                                stderr = subprocess.DEVNULL)

        p.communicate(f)


    def set_binary(self, binary_file):
        self.binary = binary_file
    
    def set_input_file(self, input_file):
        self.input_file = input_file

    def set_arch(self, arch):
        self.arch = arch
