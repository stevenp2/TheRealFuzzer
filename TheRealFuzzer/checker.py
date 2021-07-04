import csv
import json

def _is_csv(file):
    try:
        dialect = csv.Sniffer().sniff(file.read(1024))
    except:
        return False
        
    return True

def _is_json(file):
    try:
        json_file = json.load(file)
    except:
        return False
    return True

def check_type(text):
        with open(text, 'r') as f:
            if _is_json(f):
                return 'json'
            # elif is_jpeg(text):
            #     return 'jpeg'
            # elif is_elf(text):
            #     return 'elf'
            elif _is_csv(f):
                return 'csv'
            # elif is_pdf(text):
            #     return 'pdf'
            else:
                return 'txt'

def check_seg_fault(p):
    p.proc.stdin.close()
    
    if p.poll(block = True) == -11:
        return True
    
    return False