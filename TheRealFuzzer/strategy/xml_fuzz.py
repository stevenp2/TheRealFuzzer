import xml.etree.ElementTree as ET
from xml.dom import minidom
from copy import deepcopy
import re
import random

# read_xml will go through each of the attributes and 'edit' the attribute, and text
# the 'edit' will be based on how we want to fuzz it
def add_tags(Runner, root, num_tags):

    root_cpy = deepcopy(root)

    def process_add_tags(root, given_num):
        depth = depth_xml(root) 
        
        def traverse_tree(root, base, depth):
            
            if base < depth:
                for i in range(given_num):
                    if base > 0: # will prevent html section from looking bad
                        new = ET.Element('p')
                        new.text = 'YEET'
                        root.append(new)

                for child in root:
                    traverse_tree(child, base+1, depth)

            return root

        traverse_tree(root, 0, depth)
    
        return ET.tostring(root)

    for i in range(0, num_tags):
        payload = process_add_tags(root_cpy, i)
        if Runner.run_process(payload):
            return payload




def edit_elements(Runner, root):
    for child in root.iter():
        if child.attrib:
            for attrib in child.attrib:
                attr_string = child.attrib[attrib]
                child.attrib[attrib] = _format_string(attr_string)

        if child.text:
            empty_text = re.search('\\n +', child.text)

            if not empty_text:
                text_string = child.text
                child.text = _format_string(text_string)

    payload = ET.tostring(root)
    if Runner.run_process(payload):
        return payload


def bombard_tag(Runner, root):
    cpy = str(ET.tostring(deepcopy(root)))
    wideXML = ''
    for num in range(32000, 40000, 2000):
        wideXML = "{}{}".format("<p>"*num, "</p>"*num)

        if Runner.run_process(wideXML):
            return wideXML

    # return str(ET.tostring(root)) + wideXML




def shuffle_elements(Runner, root):
    
    test_range = 30000
    root_cpy = deepcopy(root)

    def iterate_process(root, num_test):
        nodes = [node for node in root.iter()] # exclude the html
        nodes_len = len(nodes) 

        for child in root:

            for i in range (0, num_test):
                rand_tag = random.randint(0, nodes_len-1)
                rand_text = random.randint(0, nodes_len-1)
                rand_attrib = random.randint(0, nodes_len-1)

                new = ET.Element(nodes[rand_tag].tag)
                new.text = nodes[rand_text].text
                new.attrib = nodes[rand_attrib].attrib

                child.append(new)

        return ET.tostring(root)
    
    for i in range(0, 1000):
        if i % 100 == 0:
            payload = iterate_process(root_cpy, i)

        if Runner.run_process(payload):
            return payload


# Helper functions

# begin from 0
def depth_xml(root):
    return max([0] + [depth_xml(child) + 1 for child in root])


def _format_string(string):
    printf_paramaters = ['%p','%n', '%s']
    str_len = len(string)

    factor = str_len / len(printf_paramaters) 
    if factor < 1:
        return random.choice(printf_paramaters)
    else:
        for i in range (0, int(factor)):
            random_loc = random.randint(0, str_len-1)
            string = string.replace(string[random_loc], random.choice(printf_paramaters))

    return string

''' For manipulation on the text
empty_text = None
        if child.text:
            empty_text = re.search('\\n +', child.text)

        if not empty_text:
            print(f'child: {child.tag, child.attrib, child.text}')
'''

''' Go through each element

    for child in root.iter():
        print(f'child: {child.tag, child.attrib, child.text}')
'''