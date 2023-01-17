__author__ = "Jon Ball"
__version__ = "Winter 2023"

import spacy
import gensim
from gensim import corpora
import pyLDAvis
from tqdm import tqdm
from collections import defaultdict
import json
import time
import os
import re

### DYNAMIC TOPIC MODELING ###
def main():
    # Load the corpus
    path_to_index = "data/txt2year.json"
    save_path = "data/ldaseq"
    print("Loading corpus...")
    print("Preparing corpus...")
    dictionary, bow_corpus, time_slice = prepare_corpus(path_to_index)
    print("Corpus prepared.")
    # Train the ldaseqmodel
    print("***\nTraining dynamic topic model...")
    t0 = time.time()
    ldaseq = gensim.models.ldaseqmodel.LdaSeqModel(
        corpus=bow_corpus,
        id2word=dictionary,
        time_slice=time_slice,
        num_topics=50,
        passes=10,
        random_state=1)
    print(f"Dynamic topic model trained in {time.time() - t0} seconds.")
    # Save the model
    print("Saving dynamic topic model...")
    ldaseq.save(save_path + "ldaseq20epochs50topics.model")
    # Visualize the model at each time slice
    for idx in range(len(time_slice)):
        doctops, topterm, dlens, tfreq, vocab = ldaseq.dtm_vis(idx, bow_corpus)
        print(f"Visualizing dynamic topic model at time slice {idx}...")
        vis_data = pyLDAvis.gensim.prepare(doctops, topterm, dlens, tfreq, vocab)
        pyLDAvis.save_html(vis_data, f"data/ldaseq/vis{idx}.html")
    print("Visualizations saved.\n***")

### PREPROCESSING FUNCTIONS ###
# Prepare corpus
def prepare_corpus(
    path_to_index: str,
    encoding: str = "utf-8"
) -> list[str]:
    # Open files by time slice
    year2paths = group_files_byyear(path_to_index)
    # Read files for each time slice
    docs = []
    time_slice = []
    print(f"...reading {len(year2paths)} time slices...")
    idx = 0
    for year, paths in sorted(year2paths.items(), key=lambda item: int(item[0])):
        idx += 1
        fiveyear = read_docs(paths, encoding)
        docs += fiveyear
        time_slice.append(len(fiveyear))
        print(f"...articles in time slice {idx+1}: {len(paths)}.")
        print(f"   ...docs: {len(fiveyear)}")
    print(f"...{len(docs)} docs read.")
    # Load the spacy model
    nlp = spacy.load("en_core_web_lg")
    nlp.add_pipe("merge_entities")
    nlp.add_pipe("merge_subtokens")
    
    # Preprocess the text files by lemmatizing
    print("Preprocessing docs...")
    preprocessed_corpus = preprocess_docs(docs, nlp)
    with open("data/preprocessed_corpus.json", "w") as outfile:
        json.dump(preprocessed_corpus, outfile)
    print("...preprocessed docs saved.")
    # Create a bow representation of the documents
    dictionary = corpora.Dictionary(preprocessed_corpus)
    bow_corpus = [dictionary.doc2bow(text) for text in preprocessed_corpus]

    return dictionary, bow_corpus, time_slice

# Preprocess the text files by lemmatizing
def preprocess_docs(
    docs: list[str],
    spacy_model
) -> list[list[str]]:
    # Lemmatize the documents
    prepped_docs = []
    for doc in tqdm(spacy_model.pipe(docs, batch_size=1000)):
        prepped_docs.append(
            [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
        )
    # Count word frequencies
    frequency = defaultdict(int)
    for doc in prepped_docs:
        for token in doc:
            frequency[token] += 1
    # Only keep words that appear five or more times
    processed_corpus = [
        [token.lower() for token in doc if frequency[token] > 5] for doc in prepped_docs
    ]

    return [tok for tok in processed_corpus if tok]

# Read files for a single time slice
def read_docs(
    paths: list,
    encoding: str = "utf-8"
) -> list[str]:
    docs = []
    for path in paths:
        with open(path, "r", encoding=encoding) as infile:
            doc = infile.read().strip()
        doc = re.sub(r"\d+", "", doc) # Remove digits
        docs += [re.sub("\s+", " ", line) for line in doc.split(sep="\n\n")] # Split into paragraphs
    return docs

# Open files by time slice
def group_files_byyear(
    path_to_index: str
    ) -> dict[str, list[str]]:
    with open(path_to_index, "r") as infile:
        yearindex = json.load(infile)
    # Walk through the input directory and find all the text files
    slices = ["1994", "1999", "2004", "2009", "2014", "2019"]
    year2paths = {slice : [] for slice in slices}
    for path, year in yearindex.items():
        if int(year) < 1995:
            year2paths["1994"].append(path)
        elif int(year) < 2000:
            year2paths["1999"].append(path)
        elif int(year) < 2005:
            year2paths["2004"].append(path)
        elif int(year) < 2010:
            year2paths["2009"].append(path)
        elif int(year) < 2015:
            year2paths["2014"].append(path)
        else:
            year2paths["2019"].append(path)
    # Filter the files by year
    return year2paths

if __name__ == "__main__":
    main()