#!/usr/bin/python3

import sys
import os
import logging


binary_path = "testfiles/"

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} [binary] [input_file]")
    exit(0)

#NOTE: change to binary = sys.argv[1]
binary = binary_path + sys.argv[1]
#NOTE: change to txt_file = sys.argv[2]
txt_file = binary_path + sys.argv[2]

if not (os.path.isfile(binary)):
    sys.exit("binary does not exist")

if not (os.path.isfile(binary)):
    sys.exit("input_file does not exist")

