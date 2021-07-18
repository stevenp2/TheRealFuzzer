import csv
import json
import xml.etree.ElementTree as ET
import subprocess


def _is_csv(file):
    try:
        file.seek(0)
        dialect = csv.Sniffer().sniff(file.read(1024))
    except:
        return False
        
    return True

def _is_json(file):
    try:
        file.seek(0)
        json_file = json.load(file)
    except:
        return False
    return True

def _is_xml(file):
    try:
        file.seek(0)
        xml_file = ET.parse(file)
    except:
        return False
    return True

def _is_txt(file):
    try:
        file.seek(0)
        txt_file = file.read()
    except:
        return False
    return True

def check_arch(input_file):
    p = subprocess.check_output(['file', f'{input_file}'])
    result = str(p)
    if 'Intel 80386' in result:
        return 'i386'
    elif 'x86-64' in result:
        return 'x86_64'

def check_type(text):
        with open(text, 'r') as f:
            if _is_json(f):
                return 'json'
            elif _is_xml(f):
                return 'xml'
            elif _is_csv(f):
                return 'csv'
            elif _is_txt(f):
                return 'txt'
            # Need more interesting strategies for below
            # elif is_jpeg(text):
            #     return 'jpeg'
            # elif is_elf(text):
            #     return 'elf'
            # elif is_pdf(text):
            #     return 'pdf'