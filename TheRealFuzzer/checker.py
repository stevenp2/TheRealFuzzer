import csv
import json
import xml.etree.ElementTree as ET


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

def check_type(text):
        with open(text, 'r') as f:
            if _is_json(f):
                return 'json'
            elif _is_xml(f):
                return 'xml'
            # elif is_jpeg(text):
            #     return 'jpeg'
            # elif is_elf(text):
            #     return 'elf'
            # elif is_pdf(text):
            #     return 'pdf'
            elif _is_csv(f):
                return 'csv'

            else:
                return 'txt'