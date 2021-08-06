import xml.etree.ElementTree as ET
from xml.dom import minidom
from copy import deepcopy
import re
import random

class XML_Fuzzer():
    def __init__(self, Runner, root, reporter):
        self.runner = Runner
        self.root = root
        self.reporter = reporter

        self.reporter.set_fuzzer('XML Fuzzer')

    def strategies(self):
        return [
            self.add_tags(100),
            self.edit_elements_format_str(),
            self.edit_elements_overflow(),
            self.bombard_tag(),
            self.shuffle_elements(100)
        ]

    # read_xml will go through each of the attributes and 'edit' the attribute, and text
    # the 'edit' will be based on how we want to fuzz it
    def add_tags(self, num_tags):
        self.reporter.set_strategy('add_tags')

        root_cpy = deepcopy(self.root)    

        depth = self.depth_xml(root_cpy) 

        
        for i in range(0, num_tags):
            payload = ET.tostring(self.traverse_tree(root_cpy, 0, depth, i))
            if self.runner.run_process(payload):
                
                return payload

    def edit_elements_format_str(self):
        self.reporter.set_strategy('edit_elements_format_str')

        # root_cpy = deepcopy(self.root)    

        for child in self.root.iter():
            if child.attrib:
                for attrib in child.attrib:
                    attr_string = child.attrib[attrib]
                    child.attrib[attrib] = self._format_string(attr_string)

            if child.text:
                empty_text = re.search('\\n +', child.text)

                if not empty_text:
                    text_string = child.text
                    child.text = self._format_string(text_string)

        payload = ET.tostring(self.root)
        if self.runner.run_process(payload):
            
            return payload

    def edit_elements_overflow(self):
        self.reporter.set_strategy('edit_elements_overflow')

        for child in self.root.iter():
            if child.attrib:
                for attrib in child.attrib:
                    attr_string = child.attrib[attrib]

                    overflow = int((2**6) / len(attr_string)) + 10
                    attr_string *= overflow
                    
                    child.attrib[attrib] = (attr_string)

            if child.text:
                empty_text = re.search('\\n +', child.text)

                if empty_text:
                    text_string = child.text
                    child.text = self._format_string(text_string)

        payload = ET.tostring(self.root)
        
        
        if self.runner.run_process(payload):
            
            return payload


    def bombard_tag(self):
        self.reporter.set_strategy('bombard_tag')

        wide_ML = ''

        for num in range(20000, 40000, 5000):
            wide_XML = "{}{}".format("<p>"*num, "</p>"*num)
            if self.runner.run_process(wide_XML):
                
                return wide_XML


    def shuffle_elements(self, num):
        self.reporter.set_strategy('shuffle_elements')
        
        root_cpy = deepcopy(self.root)

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
        
        for i in range(0, num):
            if i % 100 == 0:
                payload = iterate_process(root_cpy, i)

            
            if self.runner.run_process(payload):
                
                return payload


    # Helper functions

    # begin from 0
    def depth_xml(self, root):
        return max([0] + [self.depth_xml(child) + 1 for child in root])


    def _format_string(self, string):
        _paramaters = ['%p','%n', '%s', '%x']
        str_len = len(string)

        factor = str_len / len(_paramaters) 
        if factor < 1:
            return random.choice(_paramaters)
        else:
            for i in range (0, int(factor)):
                random_loc = random.randint(0, str_len-1)
                string = string.replace(string[random_loc], random.choice(_paramaters))

        return string

    def traverse_tree(self, root, base, depth, given_num):
                
        if base < depth:
            for i in range(given_num):
                if base > 0: # will prevent html section from looking bad
                    new = ET.Element('p')
                    new.text = 'YEET'
                    root.append(new)

            for child in root:
                self.traverse_tree(child, base+1, depth, given_num)

        return root
