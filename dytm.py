import gensim
import spacy
import json
from nltk import word_tokenize, sent_tokenize
from collections import OrderedDict
import time
import os
import re

# Open files by time slice
def group_files_byyear(path_to_index):
    with open(path_to_index, "r") as infile:
        yearindex = json.load(infile)
    # Walk through the input directory and find all the text files
    slices = ["slice9094", "slice9499", "slice0004", "slice0509", "slice1014", "slice1519"]
    year2paths = OrderedDict(slice : [] for slice in slices)
    for path, year in yearindex.items():
        if int(year) < 1995:
            year2paths["slice9094"].append(path)
        elif int(year) < 2000:
            year2paths["slice9499"].append(path)
        elif int(year) < 2005:
            year2paths["slice0004"].append(path)
        elif int(year) < 2010:
            year2paths["slice0509"].append(path)
        elif int(year) < 2015:
            year2paths["slice1014"].append(path)
        else:
            year2paths["slice1519"].append(path)
    # Sort the files by year
    txts = sorted(txts, key=lambda x: int(re.search(r"\d{4}", x).group()))
    # Filter the files by year
    txts = [t for t in txts if start_year <= int(re.search(r"\d{4}", t).group()) <= end_year]
    return txts


# Open and preprocess the text files
def preprocess_textfiles(year2paths):
    for years, paths in year2paths:
        for path in paths:
            # Read an entire article
            with open(path, "r") as infile:
                text = infile.read()
            text = text.replace("\n\n", " ").replace("\n", "")