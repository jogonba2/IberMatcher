
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
IberMatcher is a package to find the best reviewers for IberLEF task proposals. The problem definition is as follows.

We have a set of $N$ papers: $\mathcal{P} = \lbrace p_1, ..., p_N\rbrace$, and a set of $R$ reviewers: $\mathcal{R} = \lbrace r_1, ..., r_R\rbrace$. We have to found a paper-reviewer assignment $A$ as:

$A = \lbrace a_1, a_2, ..., a_N: a_i = \lbrace a_{i1}, ..., a_{ik} : a_{ij} \in \mathcal{R}\rbrace\rbrace$

where $k$ is the number of reviewers per paper.

The objective is to maximize the score $s(A)$:

$s(A) = \sum_{i=1}^{N} \sum_{j=1}^{k}\ \text{sim}(\text{categories}(a_{ij}), \text{definition}(p_i))$

subject to a set of constraints $\mathcal{C}$, where categories($a_{ij}$) is the list of research categories embeddings of the reviewer $j$ assigned to the paper $i$, and definition($p_i$) is the embedding of the $p_i$ paper's definition, e.g., title and abstract.

In this context, $sim$ can be any similarity function between a list of strings and a string. Intuitively, the best suited similarity for the paper-reviewer assignation is the maximum similarity between a research category and the paper definition, e.g.:

$sim(X, y) = \underset{\mathbf{x}\in X}{max}\; f(\mathbf{x}, \mathbf{y})$

The optimal solution to the paper-reviewer assignation is given by:

$s(A)^* = \underset{A\in \mathcal{A}}{argmax}\;S(A)$

subject to a set of constraints $\mathcal{C}$:

1. A reviewer can not be assigned to more than $l$ papers
2. A reviewer can not be more than one time to a paper
3. A reviewer can not review their own paper
4. The reviewers of a paper must be from different institutions
5. The reviewers of a paper can not pertain to the institution of the paper's authors
6. All the papers must be reviewed by $k$ reviewers

All these constraints all already integrated in IberMatch.

# 🧮 Matching algorithms
IberMatch provides three matching algorithms: **greedy**, **beam search**, and **branch and bound**.

- **Greedy**: evaluates, paper by paper, all potential reviewers and assigns to each paper the highest-ranked reviewers, ensuring feasible solutions (meeting the constraints $\mathcal{C}$). Since finding a greedy solution depends on the order of the papers and reviewers, the algorithm is repeated several times by shuffling papers and reviewers and returns the best solution if any.

- **Branch and bound**: adheres to the [classical BnB framework](https://en.wikipedia.org/wiki/Branch_and_bound) to identify optimal assignments. At each step, it evaluates the most promising solutions by employing a greedy solution as the lower bound and an optimistic upper bound derived by relaxing all constraints. This approach guides the selection of promising branches for further exploration. If a greedy solution is unavailable, the algorithm resorts to a heuristic bound calculated as $num\_papers\times reviewers\_per\_paper\times 0.4$. That is, assumes a similarity of 0.4 among all the reviewers and papers.

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
from ibermatcher.constraints import (
    unique_reviewers,
    reviewer_not_author,
    reviewer_underload,
    reviewers_from_different_institutions,
    reviewers_not_authors_institutions,
)
from functools import partial

# Load your papers and reviewer pools
papers_collection = load_papers("etc/papers_pool_abstract.xlsx")
reviewers_collection = load_reviewers("etc/reviewers_pool.xlsx")

# Define the feasibility constraints
reviewers_per_paper = 2
constraints = [
    partial(reviewer_underload, reviewers_per_paper=reviewers_per_paper),
    partial(reviewer_not_author, papers_collection=papers_collection),
    unique_reviewers,
    partial(
        reviewers_from_different_institutions,
        reviewers_collection=reviewers_collection,
    ),
    partial(
        reviewers_not_authors_institutions,
        papers_collection=papers_collection,
        reviewers_collection=reviewers_collection,
    ),
]


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
python -m ibermatcher.cli [OPTIONS] PAPERS_PATH REVIEWERS_PATH REVIEWERS_PER_PAPER MATCHER
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
