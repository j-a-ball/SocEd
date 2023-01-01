__author__ = "Jon Ball"
__verion__ = "Winter 2023"

#Dependencies: tesseract poppler
#Python 3.9.1

from pdf2image import convert_from_path
from PIL import Image
from tqdm import tqdm
import pytesseract
import argparse
import os

# Convert the PDFs to text
def convert_pdfs_to_txt(pdf_dir, txt_dir):

    pdfs = []
    for root, nodirs, files in os.walk(pdf_dir):
        for file in files:
            pdfs.append(root + "/" + file)
    
    for fpath in tqdm(pdfs):
        doc = convert_from_path(fpath)
        path, filename = os.path.split(fpath)
        basename, extension = os.path.splitext(filename)
        newfilename = os.path.join(txt_dir, basename + ".txt")
        with open(newfilename, "w") as outfile:
            for page_number, page_data in enumerate(doc):
                txt = pytesseract.image_to_string(page_data)
                outfile.write(txt)


if __name__ == "__main__":
    # Construct the argument parser and parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pdf_directory", required=True, help="path to directory containing PDFs")
    parser.add_argument("-t", "--text_directory", required=True, help="path to directory to save text files")
    args = vars(parser.parse_args())
    # Get the paths to the PDFs and text files
    pdf_dir = args["pdf_directory"]
    txt_dir = args["text_directory"]
    print("Converting PDFs to text files...\n")
    convert_pdfs_to_txt(pdf_dir, txt_dir)
    print("\nDone!")