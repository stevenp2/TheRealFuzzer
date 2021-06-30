#!/usr/bin/python3

import sys
import os
import logging
import argparse

import runner as r
import strategy

class Fuzzer():
    def __init__(self, Runner):
        runner = Runner
        pass

    def fuzz(self):
        """Return fuzz input"""
        return ""

    def run(self, runner):
        """Run `runner` with fuzz input"""
        return runner.run_process(self.fuzz())

def main(binary, text):#: runner:Runner): # takes in a runner object
    runner = r.Runner(binary, text)
    fuzzer = Fuzzer(runner)


    fuzzer.run(runner)

    return # bad.txt files


if __name__ == "__main__":
    binary_path = "../testfiles/"

    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} [binary] [input_file]")
        exit(0)

    binary = binary_path + sys.argv[1]   #NOTE: change to binary = sys.argv[1]
    txt_file = binary_path + sys.argv[2] #NOTE: change to txt_file = sys.argv[2]

    if not (os.path.isfile(binary)):
        sys.exit("binary does not exist")

    if not (os.path.isfile(binary)):
        sys.exit("input_file does not exist")

    main(binary, txt_file)



