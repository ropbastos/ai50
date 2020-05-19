import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    
    print('Sampling sum:')
    summation = 0
    for page in ranks:
        summation += ranks[page]
    print(summation)

    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    
    print('Iteration sum:')
    summation = 0
    for page in ranks:
        summation += ranks[page]
    print(summation)

    


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
    prob_dist = dict()
    # If page has no outgoing links, return equal probability for every page.
    if not corpus[page]:
        for link in corpus:
            prob_dist[link] = 1/len(corpus)
    else:
        for link in corpus:
            # Every page can be chosen at random.
            prob_dist[link] = (1-damping_factor)/len(corpus)

            # Links on current page have additional damping_factor probability of being chosen.
            if link in corpus[page]:
                prob_dist[link] += damping_factor/len(corpus[page])
        
    return prob_dist




def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Record and count samples.
    samples = dict()

    # Pick a random first page.
    current_page = random.choice(list(corpus.keys()))

    samples[current_page] = 1
    
    # Do the remaining n-1 samples.
    for _ in range(n-1):
        weights_dict = transition_model(corpus, current_page, damping_factor)

        current_page = random.choices(list(corpus.keys()), weights=weights_dict.values(), k=1)

        # random.choices() always returns a list, so current_page becomes a list of one element.
        # It needs to be a string.
        current_page = current_page[0]

        if current_page in samples:          
            samples[current_page] += 1    
        else:
            samples[current_page] = 1
    
    # Normalize sample counts
    for sample in samples:
        samples[sample] = samples[sample]/n

    return samples


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Begin by assigning every page a PR of 1/N
    ranks = dict()
    TOTAL_PAGES = len(corpus)
    for page in corpus:
        ranks[page] = 1/TOTAL_PAGES
    
    # Repeat till convergence(new ranks don't differ from previous by more than 0.001).
    CONVERGENCE_THRESHOLD = 0.001
    converged = False
    previous_ranks = ranks.copy()
    ranks_updated = 0
    while converged == False:
        # PR(p) = (1-d)/N + d*sum_i( PR(i)/NumLinks(i) )
        for page in ranks:
            ranks[page] = (1 - damping_factor)/TOTAL_PAGES

            for remaining_page, links in corpus.items():
                if not links:
                    ranks[page] += damping_factor * previous_ranks[remaining_page]/TOTAL_PAGES
                if page in links:
                    ranks[page] += damping_factor * previous_ranks[remaining_page]/len(links)
            
            ranks_updated += 1
        
        # Check for convergence.
        converged = True
        for page in ranks:
            if abs(ranks[page] - previous_ranks[page]) > CONVERGENCE_THRESHOLD:
                converged = False

        if ranks_updated == TOTAL_PAGES:
            previous_ranks = ranks.copy()
            ranks_updated = 0
    
    return ranks


if __name__ == "__main__":
    main()
