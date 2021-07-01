import subprocess

from checker import * 
from pwn import *
from strategy.csv_fuzz import *
import multiprocessing as MP


class Runner:
    def __init__(self):
        pass
            
    # Returns True if there is an segmentation fault
    def run_process(self, payload):
        # payload = self.craft_payload()
        with process(self.binary) as p:
            p.send(payload)

            if check_seg_fault(p):
                return payload


    def set_binary(self, binary_file):
        self.binary = binary_file
    
    def set_input_file(self, input_file):
        self.input_file = input_file
