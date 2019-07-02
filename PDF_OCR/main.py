import sys
import pytesseract
from pdf2image import convert_from_path
import os
from os import path
import traceback
import re
import jsonpickle
import text_parser
import json
from datetime import datetime

debug = False

def pdf2img(filename):
    return convert_from_path(filename)

def parse_pdf_file(filename):
    try:
        if not debug:
            print(filename)
            page_txt = []
            images = pdf2img(filename)

            print('Processing OCR...')
            for img in images:
                # save image for debugging
                jpg_name = filename.replace(".pdf", ".png")
                img.save(jpg_name)
                page_txt.append(ocr(img))
            
            print('Parsing...')
            comp_text = '\n\n'.join(page_txt)
            
            with open('out.txt', encoding='utf-8', mode = 'w') as outfile:
                outfile.write(comp_text)
        else:
            with open('out.txt', encoding='utf-8', mode = 'r') as infile:
                comp_text = infile.read()

        comp_group = text_parser.parse_raw_txt_to_companies(comp_text)
        print('%d companies are parsed' % len(comp_group))
        return comp_group
    except Exception as e:
        print(str(e))
        return None

def ocr(img):
    return pytesseract.image_to_string(img)

if __name__ == '__main__':
    try:
        start_time = datetime.now()
        print('----------------------------')
        print('%s Started' % start_time.strftime('%c'))
        Companies=[]
        pdf_files = []
        
        if len(sys.argv) > 1:
            path = sys.argv[1]
        else:
            path = os.getcwd()

        if  os.path.isfile(path):
            pdf_files.append(path)
        elif os.path.isdir(path):
            pdf_files = [os.path.abspath(x) for x in os.listdir(path) if x.endswith(".pdf")]
        
        if not pdf_files or len(pdf_files) == 0:
            print("No input pdf files were specified.")
            exit()

        print('%s PDF files will be parsed' % len(pdf_files))
        for pdf in pdf_files:
            comps = parse_pdf_file(pdf)
            if comps is not None:
                Companies += comps

        end_time = datetime.now()
        print('%s Ended (%s elapsed)' % (end_time.strftime('%c') , (end_time - start_time)))
        print('----------------------------')
        
        print('%d companies are parsed in total' % len(Companies))
        with open('parse_result.json', encoding='utf-8', mode = 'w') as outfile:
            outfile.write(json.dumps(json.loads(jsonpickle.encode(Companies, unpicklable=False)), indent=4))
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)