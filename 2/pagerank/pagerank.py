import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 100000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    links = corpus[page]
    if len(links) == 0: # if no links on page assign equal probablity to all pages
        equal_probability = 1 / len(corpus)
        # dict comprehension mapping file name in pages to equal probablity
        probablity_distribution = {page:equal_probability for (page, file_name) in corpus.items()}
        return probablity_distribution
    else:
        link_probability = damping_factor / len(links) + (1 - damping_factor) / len(corpus)
        random_page_in_corpus_probability = (1 - damping_factor) / len(corpus)
        probablity_distribution = corpus.copy()
        for page in probablity_distribution:
            if page in links:
                probablity_distribution[page] = link_probability
            else:
                probablity_distribution[page] = random_page_in_corpus_probability
        return probablity_distribution
    

def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page = random.choice(list(corpus.copy().keys()))
    probablity_distribution = transition_model(corpus, page, damping_factor)

    samples = list()

    for i in range(n):
        samples.append(page)
        weights = list()
        pages = list(probablity_distribution.keys())
        for page in pages:
            weights.append(probablity_distribution[page])
        page = random.choices(list(probablity_distribution.keys()), weights=weights)[0]
        probablity_distribution = transition_model(corpus, page, damping_factor)

    for page in probablity_distribution:
        probablity_distribution[page] = samples.count(page) / len(samples)
    return probablity_distribution


def divergence(previous_probablity_distribution, probablity_distribution):
    for page in previous_probablity_distribution:
        if abs(probablity_distribution[page] - previous_probablity_distribution[page]) > 0.001:
            return True
    return False


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    probablity_distribution = corpus.copy()
    equal_probability = 1 / len(corpus)
    probablity_distribution = {page:equal_probability for (page, file_name) in corpus.copy().items()}

    while True:
        previous_probablity_distribution = probablity_distribution.copy()
        for page in probablity_distribution:
            links = dict()
            for previous_page in corpus:
                if page in corpus[previous_page]:
                    links[previous_page] = previous_probablity_distribution[previous_page] / len(corpus[previous_page])
                if len(corpus[previous_page]) == 0:
                    links[previous_page] = previous_probablity_distribution[previous_page] / len(corpus)
            page_rank_of_links = 0
            for link in links:
                page_rank_of_links += links[link]
            probablity_distribution[page] = (1 / len(probablity_distribution)) * (1 - damping_factor) \
                                            + (page_rank_of_links * damping_factor)
        if not divergence(previous_probablity_distribution, probablity_distribution):
            break
    return probablity_distribution


if __name__ == "__main__":
    main()
