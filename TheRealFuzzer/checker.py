import csv

def _is_csv(file):
    try:
        file.seek(0)
        csv.Sniffer().sniff(file.read(1024))
        return True
    except csv.Error:
        return False

def check_type(text):
        with open(text) as f:
            if _is_csv(f):
                return 'csv'
            # elif is_jpeg(text):
            #     return 'jpeg'
            # elif is_elf(text):
            #     return 'elf'
            # elif is_json(text):
            #     return 'json'
            # elif is_pdf(text):
            #     return 'pdf'
            else:
                return 'txt'

def check_seg_fault(p):
    p.proc.stdin.close()
    
    if p.poll(block = True) == -11:
        return True
    
    return False