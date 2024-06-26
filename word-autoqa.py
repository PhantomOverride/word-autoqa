#!/usr/bin/env python3

try:
    from xml.etree.cElementTree import XML
except ImportError:
    from xml.etree.ElementTree import XML
import zipfile
import json
import re
import argparse
from os import listdir
from os.path import isfile, join, dirname


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def get_docx_text(path):
    WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    PARA = WORD_NAMESPACE + 'p'
    TEXT = WORD_NAMESPACE + 't'

    try:
        document = zipfile.ZipFile(path)
        xml_content = document.read('word/document.xml')
        document.close()
    except:
        print("[ ! ] Error, could not open file", path)
        exit(1)

    tree = XML(xml_content)

    paragraphs = []
    #for paragraph in tree.getiterator(PARA): # getiterator is deprecated
    for paragraph in tree.iter(PARA):
        texts = [node.text
                 #for node in paragraph.getiterator(TEXT) # getiterator is deprecated
                 for node in paragraph.iter(TEXT)
                 if node.text]
        if texts:
            paragraphs.append(''.join(texts))

    return '\n\n'.join(paragraphs)


def get_rules(path):
    rules = []
    files = [f for f in listdir(path) if isfile(join(path, f))]
    for file in files:
        try:
            with open(path+file) as f:
                contents = f.read()
                rules += json.loads(contents)["rules"]
        except:
            print("[ ! ] Could not process file", path+file, ", skipping...")

    return rules

def validate(text, rules, passing=False):
    passed = failed = 0

    for rule in rules:
        match = re.findall(rule["find"], text)
        if match:
            failed += 1
            print(bcolors.FAIL, rule.get("fail-message", "Rule fail text not set"), "(\"" + match[0] + "\" from pattern \"" + rule.get("find") + "\")", "[", len(match), "]",bcolors.ENDC)
        else:
            passed += 1
            if passing:
                print(bcolors.OKGREEN, rule.get("pass-message","Rule pass text not set"), bcolors.ENDC)

    print("[ + ] Finished.", passed, "rules passed,", failed, "failed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate document text against a set of rules.")
    parser.add_argument("file", nargs='+', help='Name of DOCX file(s)')
    parser.add_argument("-c", "--no-color", help="Do not use terminal colours", action="store_true")
    parser.add_argument("-p", "--passing", help="Print success messages for rules that do not match", action="store_true")
    args = parser.parse_args()

    if ( args.no_color ):
        bcolors.HEADER = ''
        bcolors.OKBLUE = ''
        bcolors.OKGREEN = ''
        bcolors.WARNING = ''
        bcolors.FAIL = ''
        bcolors.ENDC = ''
        bcolors.BOLD = ''
        bcolors.UNDERLINE = ''

    if(len(args.file)>1):
        print("[ + ] Validating",len(args.file),"files.")
        print("[ + ]" + "-"*70)

    for somefile in args.file:
        print("[ + ] Running validation rules against file", somefile)
        text = get_docx_text(somefile)
        rules = get_rules(join(dirname(__file__), "rules/"))
        validate(text, rules, args.passing)
        if(len(args.file)>1):
            print("[ + ] " + "-"*70)
    
    if(len(args.file)>1):
        print("[ + ] Finished validating",len(args.file),"files.")