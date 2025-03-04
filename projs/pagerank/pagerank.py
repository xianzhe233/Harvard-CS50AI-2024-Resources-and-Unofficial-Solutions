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
    # ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    # print(f"PageRank Results from Sampling (n = {SAMPLES})")
    # for page in sorted(ranks):
    #     print(f"  {page}: {ranks[page]:.4f}")
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
        pages[filename] = set(link for link in pages[filename] if link in pages)

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    new_pages = corpus[page]
    pages_length = len(new_pages)
    all_pages = corpus.keys()
    all_pages_length = len(all_pages)
    random_prob = (1 - damping_factor) / all_pages_length

    if pages_length > 0:
        # for every new page,
        # P(p_i) = D * 1 / pages_length + (1 - D) * 1 / all_pages_length
        #         { pick from new ones }  {       randomly choose       }
        surf_prob = (damping_factor / pages_length)
        surf_distribution = {new_page: surf_prob for new_page in new_pages}
        # each of other pages has a randomly choosing probability
        for p in all_pages:
            if p in new_pages:
                surf_distribution[p] += random_prob
            else:
                surf_distribution[p] = random_prob
    else:
        # if there's no links, just use uniform distribution
        surf_distribution = {new_page: random_prob for new_page in all_pages}

    return surf_distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page_values = {page: 0 for page in corpus.keys()}
    page = random.choice(list(page_values.keys()))

    # randomly picking a starting page used 1 sample
    for _ in range(n - 1):
        page_values[page] += 1
        transition_dict = transition_model(corpus, page, damping_factor)
        pages = transition_dict.keys()
        distribution = transition_dict.values()
        page = random.choices(list(pages), list(distribution), k=1)[0]

    sample_dict = {p: v / n for p, v in page_values.items()}
    return sample_dict


def iterate_pagerank(corpus, damping_factor, threshold=0.001):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Returns a set of all pages that link to page.
    def pages_link_to(page):
        return set(
            p for p, pages in corpus.items() if page in pages or not pages)

    # Updates PR(p), returns new pagerank and changed value.
    def pagerank_update(page):
        new_pagerank = (1 - damping_factor) / n
        for i in pages_link_to(page):
            numlinks = len(corpus[i])
            numlinks = n if numlinks == 0 else numlinks
            new_pagerank += damping_factor * page_ranks[i] / numlinks
        diff = abs(new_pagerank - page_ranks[page])
        return new_pagerank, diff

    # initialize page_rank of all pages
    n = len(corpus.keys())
    page_ranks = {page: 1 / n for page in corpus.keys()}
    pagerank_updates = page_ranks.copy()

    while True:
        max_diff = 0
        for p in corpus.keys():
            pagerank, diff = pagerank_update(p)
            max_diff = max(max_diff, diff)
            pagerank_updates.update({p: pagerank})
        if max_diff <= threshold:
            break
        else:
            page_ranks.update(pagerank_updates)

    return page_ranks


if __name__ == "__main__":
    main()
