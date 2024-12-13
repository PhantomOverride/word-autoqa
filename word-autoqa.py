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
    BLACK = '\033[30m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BGWHITE = '\033[44m'
    BGYELLOW = '\033[103m'


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
    for paragraph in tree.iter(PARA):
        texts = [node.text
                 for node in paragraph.iter(TEXT)
                 if node.text]
        if texts:
            paragraphs.append(''.join(texts))

    return '\n\n'.join(paragraphs)


def get_rules(path):
    rules = []
    files = [f for f in listdir(path) if isfile(join(path, f)) and f.endswith('.json')]
    for file in files:
        try:
            with open(path+file) as f:
                contents = f.read()
                current_rules = json.loads(contents)["rules"]
                for r in current_rules:
                    r["source"] = file # Append the file name as the source attribute for each rule
                rules += current_rules
        except:
            print("[ ! ] Could not process file", path+file, ", skipping...")
    return rules


def validate(text, rules, passing=False, context=False):
    passed = failed = 0
    
    for rule in rules:
        match = re.findall(rule["find"], text)
        if context: # Yes, it's inefficient to do two searches. But I'm lazy and this feature is an afterthought.
            ctx = list(re.finditer(rule["find"], text))
        if match: #todo implement behaviour based on rule confidence
            failed += 1
            print(bcolors.FAIL + "[ ! ]", "["+rule.get("source", "Rule source not set")+"]", rule.get("fail-message", "Rule fail text not set"), "(\"" + match[0] + "\" from pattern \"" + rule.get("find") + "\")", "[", len(match), "]",bcolors.ENDC)
            if context and ctx: # Print context if user wants it (-x flag)
                ctx_counter = 0
                for ctx_match in ctx: # Perform for each occurance
                    ctx_counter+=1
                    start, end = ctx_match.start(), ctx_match.end()
                    context_size = 30
                    
                    context_start = max(0, start - context_size) # Do not exceed source bounds
                    context_end = min(len(text), end + context_size) # Do not exceed source bounds
                    context_text = text[context_start:context_end]
        
                    print("  [ Match", ctx_counter, "] " , "-"*70)
                    
                    #Inject colour sequences. This will not work if match contains a newline due to the section below
                    ctx_colour_start = start-context_start
                    ctx_colour_end = (end-context_start) + len(bcolors.BLACK+ bcolors.BGYELLOW)
                    context_text = context_text[:ctx_colour_start] + bcolors.BLACK + bcolors.BGYELLOW + context_text[ctx_colour_start:]
                    context_text = context_text[:ctx_colour_end] + bcolors.ENDC + bcolors.WARNING + context_text[ctx_colour_end:]

                    # Want to print with colour and indentation, but context_text may contain linebreaks
                    context_text_lines = context_text.splitlines()
                    for context_text_line in context_text_lines:
                        print(bcolors.WARNING + "    " + context_text_line, bcolors.ENDC)

                    #print("  [ End", ctx_counter, "] " , "-"*70, "\n")
                    print("\n")

        else:
            passed += 1
            if passing:
                print(bcolors.OKGREEN + "[ + ]", "["+rule.get("source", "Rule source not set")+"]", rule.get("pass-message","Rule pass text not set"), bcolors.ENDC)

    print("[ + ] Finished.", passed, "rules passed,", failed, "failed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate document text against a set of rules.")
    parser.add_argument("file", nargs='+', help='Name of DOCX file(s)')
    parser.add_argument("-c", "--no-color", help="Do not use terminal colours", action="store_true")
    parser.add_argument("-p", "--passing", help="Print success messages for rules that do not match", action="store_true")
    parser.add_argument("-x", "--context", help="Print context for each match", action="store_true")
    args = parser.parse_args()

    if ( args.no_color ):
        bcolors.HEADER = ''
        bcolors.OKBLUE = ''
        bcolors.OKGREEN = ''
        bcolors.WARNING = ''
        bcolors.BLACK = ''
        bcolors.FAIL = ''
        bcolors.ENDC = ''
        bcolors.BOLD = ''
        bcolors.UNDERLINE = ''
        bcolors.BGWHITE = ''
        bcolors.BGYELLOW = ''

    if(len(args.file)>1):
        print("[ + ] Validating", len(args.file), "files.")
        print("[ + ] " + "-"*90)

    for somefile in args.file:
        print("[ + ] Running validation rules against file", somefile)
        text = get_docx_text(somefile)
        rules = get_rules(join(dirname(__file__), "rules/"))
        validate(text, rules, passing=args.passing, context=args.context)
        if(len(args.file)>1):
            print("[ + ] " + "-"*90)
    
    if(len(args.file)>1):
        print("[ + ] Finished validating",len(args.file),"files.")
