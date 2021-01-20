import nltk
import sys
import os
import math
import string

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    while True:
        # Prompt user for query
        query = set(tokenize(input("Query: ")))

        # Determine top file matches according to TF-IDF
        filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

        # Extract sentences from top files
        sentences = dict()
        for filename in filenames:
            for passage in files[filename].split("\n"):
                for sentence in nltk.sent_tokenize(passage):
                    tokens = tokenize(sentence)
                    if tokens:
                        sentences[sentence] = tokens

        # Compute IDF values across sentences
        idfs = compute_idfs(sentences)

        # Determine top sentence matches
        matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
        for match in matches:
            print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    files = {
        file: open(os.path.join(directory, file), encoding="utf-8").read()
        for file in os.listdir(directory)
        if file.endswith(".txt")
    }
    return files


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    words = nltk.word_tokenize(document.lower())
    stop_words = nltk.corpus.stopwords.words("english")
    words = [
        word for word in words
        if not word in stop_words
        and word.islower()
    ]
    return words

def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    words = set()
    for file in documents:
        words.update(documents[file])
    idfs = dict()
    for word in words:
        x = len(documents) / sum(word in documents[file] for file in documents)
        idf = math.log(x)
        idfs[word] = idf
    return idfs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    tf_idfs = { file: 0 for file in files }
    for word in query:
        for file in files:
            if word in files[file]:
                tf_idf = idfs[word] * sum(word == file_word for file_word in files[file])
                tf_idfs[file] += tf_idf
    # sort the tf_idfs by value
    tf_idfs = {file: tf_idf for file, tf_idf in sorted(tf_idfs.items(), \
                                                    key=lambda item: item[1], reverse=True)}
    # return the top n files
    return list(tf_idfs.keys())[:n]


def query_density(query, sentence):
    """
    Returns the query density of the sentence.
    Query term density is defined as the proportion of words in the sentence
    that are also words in the query. For example, if a sentence has 10 words,
    3 of which are in the query, then the sentence's query term density is `0.3`.
    """
    return len([word for word in sentence if word in query]) / len(sentence)

def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    # TODO: sort by term density
    sentence_idfs = { sentence: 0 for sentence in sentences }
    for sentence in sentences:
        for word in query:
            if word in sentences[sentence]:
                sentence_idfs[sentence] += idfs[word]

    # sort the sentence_idfs by value
    sorted_sentences = list()
    idf_values = sentence_idfs.values()
    while len(sorted_sentences) < len(sentences):
        max_idf = max(idf_values)

        # get all sentences with equal value and sort them by query density (qd)
        equal_sentences = []
        for sentence in sentence_idfs:
            if sentence_idfs[sentence] == max_idf:
                equal_sentences.append(sentence)
        # get all query densities (qd) of equal sentences
        equal_sentences_qd = []
        for sentence in equal_sentences:
            equal_sentences_qd.append(query_density(query, sentences[sentence]))
        while len(equal_sentences) > 0:
            max_query_density = max(equal_sentences_qd)
            max_query_density_sentence = equal_sentences[equal_sentences_qd.index(max_query_density)]
            # add items to sorted sentences
            sorted_sentences.append(max_query_density_sentence)
            # remove items from lists now that they are sorted
            equal_sentences.remove(max_query_density_sentence)
            equal_sentences_qd.remove(max_query_density)
    # return the top n sentences
    return sorted_sentences[:n]


if __name__ == "__main__":
    main()
