
<!---
Copyright 2025 Symanto
From Symanto to IberLEF with ❤️

Licensed under the CC BY-SA 4.0 License

https://creativecommons.org/licenses/by-sa/4.0
-->

<h1 align="center">🐾 IberMatcher </h1> 
<p align="center">
    <a href="LICENSE">
        <img alt="license" src="https://img.shields.io/badge/License-Apache_2.0-green">
    </a>
    <a href="CODE_OF_CONDUCT.md">
        <img alt="Contributor Covenant" src="https://img.shields.io/badge/Contributor%20Covenant-v2.0-green">
    </a>
    <img alt="Python version" src="https://img.shields.io/badge/Python-3.10-blue">
</p>

<h3 align="center">
    <p><b>Optimal matching among reviewers and papers</b></p>
    From Symanto to IberLEF with ❤️
</h3>

# 📖 Introduction
IberMatcher is a package to find the best reviewers for IberLEF task proposals. The core problem can be described as follows.

Given a set of $N$ papers $\mathcal{P} = \lbrace p_1, p_2, \ldots, p_N \rbrace$ and a set of $R$ reviewers $\mathcal{R} = \lbrace r_1, r_2, \ldots, r_R \rbrace$, the goal is to determine an assignment $A$ that optimally matches $k$ reviewers to each paper:

$$
A = \lbrace a_1, a_2, \ldots, a_N : a_i = \lbrace a_{i1}, \ldots, a_{ik} : a_{ij} \in \mathcal{R} \rbrace \rbrace
$$

The goal is to maximize the total assignment score $s(A)$, given by:

$$
s(A) = \sum_{i=1}^{N} \sum_{j=1}^{k} f(a_{ij}, p_i)
$$

where $f: \mathcal{R}\times\mathcal{P} \rightarrow \mathbb{R}$ measures the suitability of the reviewer $a_{ij}$ for the paper $p_i$. $f$ is derived from a similarity measure $\textrm{sim}$ applied to the embeddings of reviewers and papers. In IberMatcher, $f$ is defined as follows:

$$
f(X, \mathbf{y}) = \max_{\mathbf{x} \in X} \text{sim}(\mathbf{x}, \mathbf{y})
$$

where:
- $X$ represents the set of research category embeddings for a reviewer.
- $\mathbf{y}$ is the embedding of a paper (e.g., derived from its title and abstract).
- $\text{sim}(\mathbf{x}, \mathbf{y})$ computes the cosine similarity between embeddings $\mathbf{x}$ and $\mathbf{y}$.

The optimal assignment $A^*$ is then defined as:

$$
A^* = \underset{A \in \mathcal{A}}{\arg\max}\ s(A)
$$

where $\mathcal{A}$ is the set of all feasible assignments satisfying a set of constraints $\mathcal{C}$, which ensure the fairness of the assignments:

1. **Paper review limits**: each paper $p_i$ must be assigned exactly to $k$ reviewers:
$$
|a_i|=k,\quad \forall i\in\lbrace 1\ldots, N\rbrace
$$
2. **Reviewer capacity**: a reviewer $r_j$ cannot be assigned to more than $l$ papers:
$$
|\lbrace i : r_j \in a_i\rbrace|\leq l\quad \forall j\in\lbrace 1,\ldots, R\rbrace
$$
3. **Unique reviewers per paper**: a reviewer cannot be assigned to the same paper multiple times:
$$
a_{ij}\neq a_{ij^{'}}\quad \forall i\in\lbrace 1\ldots, N\rbrace, j\neq j^{'}
$$
4. **Reviewer conflict restrictions**: restrictions related to conflicts of interest implying authorship and institutions.
   * A reviewer cannot be assigned to review their own paper.
   * Reviewers assigned to the paper $p_i$ must belong to different institutions.
   * Reviewers assigned to the paper $p_i$ must not belong to the same institution as any of $p_i$'s authors.
   
All these constraints all already integrated in IberMatcher. IberMatcher provides three strategies to find the optimal assignment $A^*$.

# 🧮 Matching algorithms
IberMatcher provides three matching algorithms: **greedy**, **beam search**, and **branch and bound**.

- **Greedy**: evaluates, paper by paper, all potential reviewers and assigns to each paper the highest-ranked reviewers, ensuring feasible solutions (meeting the constraints $\mathcal{C}$). Since finding a greedy solution depends on the order of the papers and reviewers, the algorithm is repeated several times by shuffling papers and reviewers and returns the best solution if any.

- **Branch and bound**: adheres to the [classical BnB framework](https://en.wikipedia.org/wiki/Branch_and_bound) to identify optimal assignments. At each step, it evaluates the most promising solutions by employing a greedy solution as the lower bound and an optimistic upper bound derived by relaxing all constraints. This approach guides the selection of promising branches for further exploration. If a greedy solution is unavailable, the algorithm resorts to a heuristic bound calculated as $numpapers\times reviewersperpaper\times 0.4$. That is, assumes a similarity of 0.4 among all the reviewers and papers.

- **Beam search**: implemented as branch and bound when the lower bound is 0 and the size of the priority queue is limited to a maximum number of items.

# 🛠️ Installation
Just install all the required packages with:

```bash
pip install -r requirements.txt
```

# 👨🏻‍💻 Usage
You can use IberMatcher through the command line or programmatically.

Although not necessary for the programmatic usage, it is recommended to format your papers and reviewers pools using excel files.

> [!TIP] 
> For **papers**, the columns `title`, `contact`, `email`, `authors`, `institutions`, and `countries` are mandatory, and all of them must be *strings*. The columns `authors`, `institutions`, and `countries` must be strings with items separated with `\n`. </br></br>For **reviewers**, the columns `full_name`, `institution`, `country`, `email`, `categories` are mandatory, and all of them must be *strings*. The column `categories` must be a string of categories separated with `;`.

## </> Programmatic
Here you have the full control for using IberMatcher. You load the pools, define any constraint, and parameterize the matching algorithms as you prefer. Here is an example:

```python
from ibermatcher.cli_utils import load_papers, load_reviewers
from ibermatcher.matchers import (
    match_by_greedy,
    match_by_beam_search,
    match_by_branch_and_bound,
)
from ibermatcher.constraints import get_constraints

# Load your papers and reviewer pools
papers_collection = load_papers("etc/papers_pool.xlsx")
reviewers_collection = load_reviewers("etc/reviewers_pool.xlsx")

# Define the feasibility constraints
reviewers_per_paper = 2
constraints = get_constraints(
    [
        "reviewer_underload",
        "reviewer_not_author",
        "unique_reviewers",
        "reviewers_from_different_institutions",
        "reviewers_not_authors_institutions",
    ],
    papers_collection,
    reviewers_collection,
    reviewers_per_paper,
)

# Match using greedy matcher
solution, score = match_by_greedy(
    papers_collection,
    reviewers_collection,
    constraints,
    reviewers_per_paper,
    iters=5000,
)
print(solution, score)

# Match using beam search
solution, score = match_by_beam_search(
    papers_collection,
    reviewers_collection,
    constraints,
    reviewers_per_paper,
    beam_size=10,
)
print(solution, score)

# Match using Branch and Bound (can take a lot of time for complex setups)
solution, score = match_by_branch_and_bound(
    papers_collection,
    reviewers_collection,
    constraints,
    reviewers_per_paper,
)
print(solution, score)
```

## 📟 CLI
From CLI, you must specify two excel files, the number of reviewers per paper and the matcher (`greedy`, `branch_and_bound`, or `beam_search`).

```bash
Usage: python -m ibermatcher.cli [OPTIONS] PAPERS_PATH REVIEWERS_PATH                                                                                                   
                                  REVIEWERS_PER_PAPER MATCHER                                                                                                            
                                                                                                                                                                         
╭─ Arguments ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    papers_path              TEXT     Path to the papers pool (excel file) [default: None] [required]                                                                │
│ *    reviewers_path           TEXT     Path to the reviewers pool (excel file) [default: None] [required]                                                             │
│ *    reviewers_per_paper      INTEGER  Number of reviewers per paper [default: None] [required]                                                                       │
│ *    matcher                  TEXT     Matcher name [default: None] [required]                                                                                        │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --constraint-names        TEXT  Names of the constraints                                                                                                              │
│ --help                          Show this message and exit.                                                                                                           │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

## 📤 Assignment example
To illustrate how the output looks like, here is an example of alignment, computed with the greedy algorithm, for IberLEF 2025. Do you agree with it? 😋:

```json
{
   "ESPANTE: Spanish Text-to-Triples and Triples-to-Text Generation":[
      "María Estrella Vallecillo Rodríguez",
      "Marco Antonio Sobrevilla Cabezudo"
   ],
   "DIMEMEX@IberLEF2025 Detection of Inappropriate MEmes from MEXico":[
      "Gemma Bel-Enguix",
      "María Estrella Vallecillo Rodríguez"
   ],
   "CLEARS: Challenge for Plain Language and Easy-to-Read Adaptation for Spanish texts":[
      "Julio Gonzalo",
      "Francisco Rangel"
   ],
   "Rest-Mex 2025: Researching on Evaluating Sentiment and Textual instances selection for Mexican magical towns":[
      "Jorge Carrillo de Albornoz",
      "Rafael Valencia García"
   ],
   "TA1C: Te Ahorré Un Click - Clickbait detection and spoiling competition in Spanish":[
      "Begoña Altuna",
      "Paolo Rosso"
   ],
   "FeSQuA: Few-Shot Question Answering":[
      "Martin Krallinger",
      "Ulisses B. Corrêa"
   ],
   "HomoLAT: Human-centric polarity detection in Online Messages Oriented to the Latin American-speaking LGBTQ+ population":[
      "Francisco García",
      "Paolo Rosso"
   ],
   "SatiSPeech: Multimodal Audio-Text Satire Classification in Spanish":[
      "Aiala Rosá",
      "Gemma Bel-Enguix"
   ],
   "ADoBo 2025: A shared task on Automatic Detection of Borrowings":[
      "Marvin Agüero Torales",
      "Rafael Valencia García"
   ],
   "DE FACTO: Factuality and Accuracy Challenge for Text Outputs":[
      "Areg Mikael Sarvazyan",
      "Hugo Jair Escalante"
   ],
   "HOPE at IberLEF 2025: Optimism, Expectations or Sarcasm?":[
      "Pablo Moral Martín",
      "Hugo Jair Escalante"
   ],
   "Social Support at IberLEF 2025:Social Support Detection from Social Media Texts":[
      "Fazlourrahman Balouchzahi",
      "Manuel Montes y Gómez"
   ],
   "PRESTA: Preguntas y Respuestas sobre Tablas en Español (Questions and Answers about Tables in Spanish)":[
      "Julio Gonzalo",
      "Begoña Altuna"
   ],
   "MiSongGyny: Misogyny in Song Lyrics":[
      "Manuel Montes y Gómez",
      "Arturo Montejo Ráez"
   ],
   "MiMIC: Multi-Modal AI Content Detection":[
      "Delia Irazú Hernández Farías",
      "Pablo Moral Martín"
   ],
   "Aspect Sentiment Quad Prediction in Portuguese":[
      "Jorge Carrillo de Albornoz",
      "José Antonio García Díaz"
   ],
   "MentalRiskES 2025 Early detection of mental disorders risk in Spanish Third edition - Detecting Addiction":[
      "Delia Irazú Hernández Farías",
      "Fazlourrahman Balouchzahi"
   ],
   "PastReader 2025 IberLEF Task on Transcription of Historical Content First edition - Transcribing texts from the past":[
      "Helena Gómez Adorno",
      "Alba Bonet"
   ]
}
```

# 🤝 Contributing
Please, use `dev-tools` to contribute to this repo.
