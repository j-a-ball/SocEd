__author__ = "Jon Ball"
__verion__ = "Winter 2023"

# Python 3.9.1

from gensim.models import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import spacy
from tqdm import tqdm

from collections import defaultdict
import json
import time
import os
import re

from eric_parser import ERICParser

# Main function
def main():
    # Load the .xml files representing the ERIC database (https://eric.ed.gov/?download)
    paths = xml_paths("eric_data")
    # Parse the files and save a document for each ISSN, with abstracts split by "\n\n"
    issn2doc = parse_eric_xmls(paths)
    # Process the data and save as Gensim TaggedDocuments
    corpus = process_docs(issn2doc)
    # Train the model
    model = train_model(corpus)
    # Visualize the model
    visualize_model(model)

def visualize_model(
    model: Doc2Vec,
    output_dir: str = "data/vsm/"
    ) -> None:
    """Given a trained doc2vec model, visualize the model."""
    # Get the vectors
    print("Retrieving doc vectors...")
    vectors = model.docvecs.vectors_docs
    # Reduce the dimensionality of the vectors
    print("   ...reducing to 2 principal components...")
    pca = PCA(n_components=2)
    vectors = pca.fit_transform(vectors)
    # Save the vector space
    print("   ...saving reduced vector space...")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    np.save(output_dir + "vectors.npy", vectors)
    # Cluster the vectors
    print("   ...clustering with k-means...")
    kmeans = KMeans(n_clusters=10)
    kmeans.fit(vectors)
    # Plot the vectors
    plt.scatter(vectors[:, 0], vectors[:, 1], c=kmeans.labels_, cmap="rainbow")
    # Add the ISSN labels
    for i, issn in enumerate(model.docvecs.doctags):
        plt.annotate(issn, (vectors[i, 0], vectors[i, 1]))
    # Show the plot
    print("Plot prepared.")
    plt.show()
    # Save the plot
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    plt.savefig(output_dir + "vsm.png", bbox_inches="tight", dpi=1000)  
    print("Plot saved.\n***"))        

# Train the doc2vec model with logging
# Hyperparameters are based on previous usage of doc2vec with the ERIC corpus
def train_model(
    corpus: list[TaggedDocument]
    ) -> Doc2Vec:
    """Given a list of TaggedDocuments, train a doc2vec model."""
    # Initialize the model
    print("Initializing the doc2vec model...")
    model = Doc2Vec(
        vector_size=100,
        window=5,   
        min_count=5,
        workers=8,
        epochs=10,
        seed=1
    )
    # Build the vocabulary
    print("Building the vocabulary...")
    model.build_vocab(corpus)
    # Train the model
    print("Training the model...")
    tock = time.time()
    model.train(corpus, total_examples=model.corpus_count, epochs=model.epochs)
    print(f"Model trained in {time.time() - tock} seconds.")
    return model

# Tokenize the documents and return a list of TaggedDocuments
def process_docs(
    docs: dict[str : str],
    ) -> list[TaggedDocument]:
    """Given a dictionary of documents, return a list of TaggedDocuments."""
    # Convert the data dict to a list of TaggedDocuments
    tagged_docs = []
    # Spacy for tokenization
    nlp = spacy.load("en_core_web_sm")
    for issn, doc in docs.items():
        # Split the document into abstracts
        abstracts = doc.split("\n\n")
        # Tokenize the entire document in chunks
        tokenized_abstracts = [token.text for abstract in tqdm(abstracts) for token in nlp(abstract)]
        # Add the document to the list of TaggedDocuments
        tagged_docs.append(TaggedDocument(tokenized_abstracts, [issn]))
    return tagged_docs

# Parse the .xml files into a dictionary mapping ISSNs to documents
def parse_eric_xmls(
    paths_to_xml: list[str],
) -> dict[str : str]:
    """Given a list of paths to .xml files, parse the files and return a list of TaggedDocuments."""
    eric_parser = ERICParser()
    issn2doc = defaultdict(str)
    for path in paths_to_xml: # For each year's ERIC .xml file
        # Parse the .xml file
        eric_parser.parse(path)
        # Iterate over item records
        for record in eric_parser.iter_metadata():
            # Pull abstract of record
            description = record.xpath("dc:description", namespaces=eric_parser.nsmap)[0].text
            description = clean_string(description)
            # Pull ISSN of record
            issn = record.xpath("eric:issn", namespaces=eric_parser.nsmap)[0].text.strip()
            if description and issn:
                # Add the abstract to the dictionary of documents for a given ISSN
                issn2doc[issn] += description + "\n\n" 
    print(f"{len(issn2doc)} unique ISSNs found.")
    return issn2doc

def clean_string(s: str):
    """Given a string, return a cleaned version of the string."""
    # Remove parentheses and their contents at the end of strings
    s = re.sub(r"\([\S\s]{,50}\)\.?$", "", s)
    # Remove HTML tags
    s = re.sub(r"<.*?>", " ", s)
    # Remove non-ASCII characters
    s = re.sub(r"[^\x00-\x7F]+", " ", s)
    # Remove extra whitespace
    s = re.sub(r"\s+", " ", s)
    # Remove leading and trailing whitespace
    return s.strip()

# Walk the directory tree and return a list of paths to .xml files
def xml_paths(
    relpath: str = "eric_data",
    ) -> list[str]:
    """Given a relative path, return a list of paths to .xml files."""
    paths_to_xml = []
    for path, dirs, files in os.walk(relpath):
        for file in files:
            if re.search("9[0-9].xml|0[0-9].xml|1[0-9].xml", file): # 1990-2019
                paths_to_xml.append(os.path.join(path, file))
    return paths_to_xml