__author__ = "Jon Ball"
__version__ = "Winter 2023"

from collections import Counter, defaultdict
from tqdm import tqdm
import argparse
import string
import spacy
import json
import re
import os


def get_filenames(input_dir):
    # Walk through the input directory and find all the text files
    txts = []
    for root, nodirs, files in os.walk(input_dir):
        for file in files:
            if re.search(r"\.txt$", file):
                txts.append(root + "/" + file)
    return txts


def author_scan(line):
    # Scan for authors in a line of text, cleaning the results
    # Many author names are separated by semicolons
    newline = line.replace(";", " ")

    doc = nlp(newline)
        
    auts = []
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            auts.append(ent.text)
                
    clean = []
    subnames = []
    for aut in auts:
        # First name, last name is clean
        if re.search("[A-Za-z]\s[A-Za-z]{2,}", aut):
            clean.append(aut)
        # Initial splitting the first and last name is clean
        elif re.search("\s[A-Z]\.?\s", aut):
            clean.append(aut)
        # Everything else is a first or last name
        else:
            subnames.append(aut)
        
    # Combine subnames
    for last, first in zip(subnames[::2], subnames[1::2]):
        clean.append(" ". join((first, last)))

    # Remove punctuation except for hyphens
    punct = string.punctuation[:12] + string.punctuation[13:]

    return list(set(
        [a.translate(str.maketrans('', '', punct)) for a in clean]
        ))


def citation_scan(txt):
    # Return the primary and cited authors from a text file
    # as well as year of publication and cited journals
    with open(txt, "r") as rfile:
        lines = rfile.read().split(sep="\n\n")
    
    # Scan the first 10 lines for primary authors and year of publication
    primary_authors = []
    for line in lines[:10]:
        primary_authors += [re.sub(r"\n.+", "", a).strip().lower() for a in author_scan(line)]
    for line in lines[:10]:
        year = re.search(r"\d{4}", line)
        if year:
            year = year.group()
            break

    # Scan the last few pages for cited authors and journals
    cited_authors = []
    cited_journals = []
    for line in lines[-150:]:
        
        if re.search(r"\d{4}[a-z]?\.", line):
            authors = re.search(r"^[\w\W]*\.(?=\s\d{4})", line) # Find author names listed before year
            if authors:
                group = authors.group()
                group = group.replace("\n", " ").replace(", eds.", "")
                # Remove line breaks and editor designations
                cited_authors += [a.strip().lower() for a in author_scan(group)]

            journal = re.search(r"\.\"\s([^\d]+)\d", line) # Find journal name following article title
            if journal:
                group = journal.group(1)
                group = group.replace("\n", " ").replace(" ", "").replace("-", "")
                # Remove line breaks, spaces, and dashes
                cited_journals.append(group.strip().lower())

    return {
        "primary_authors": primary_authors,
        "cited_authors": cited_authors,
        "cited_journals": cited_journals,
        "year": year,
        }


def main(input_dir, output_dir):

    txts = get_filenames(input_dir)
    print(f"{len(txts)} text files found in input directory. Scanning for citations...")

    citeD = defaultdict(list)
    all_authors = set()
    txt2year = {}
    journals = []

    for txt in tqdm(txts):
        d = citation_scan(txt)
        # Save a mapping of text file to year of publication
        txt2year[txt] = d["year"]
        # Save a mapping of primary authors to cited authors
        for author in d["primary_authors"]:
            citeD[author] += d["cited_authors"]
        # Save a set of all cited authors
        all_authors.update(d["cited_authors"])
        # Save a list of all cited journals
        journals += d["cited_journals"]

    print(f"{len(all_authors)} authors cited.")
    print(f"{len(set(journals))} journals cited.\n")

    print("Saving json mapping of text file to year of publication...")
    with open(output_dir + "/txt2year.json", "w") as wfile:
        json.dump(txt2year, wfile)

    print("Saving author citation data...")
    with open(output_dir + "/author_citations.json", "w") as wfile:
        json.dump(
            {k: v for k, v in citeD.items() if k in all_authors}, 
            wfile)

    print("Saving count mapping of all cited journals...")
    with open(output_dir + "/cited_journals.json", "w") as wfile:
        json.dump(Counter(journals), wfile)

    print("\nDone.\n**********\n")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_dir", help="Input directory of text files")
    parser.add_argument("-o", "--output_dir", help="Output directory for preprocessed text files")
    args = parser.parse_args()

    nlp = spacy.load("en_core_web_lg")

    main(args.input_dir, args.output_dir)