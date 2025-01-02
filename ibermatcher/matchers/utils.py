from queue import PriorityQueue
from random import shuffle
from typing import Callable, Literal

import numpy as np

from ..types import Paper, PriorityEntry, Reviewer


def sim_pairwise(
    X: np.ndarray, y: np.ndarray, aggregation: Literal["max", "mean"] = "max"
) -> float:
    X_norm = X / np.linalg.norm(X, axis=1, keepdims=True)
    y_norm = y / np.linalg.norm(y)

    similarities = X_norm @ y_norm.T

    if aggregation == "max":
        return similarities.max().item()
    elif aggregation == "mean":
        return similarities.mean().item()
    else:
        raise ValueError("Invalid aggregation method. Choose 'max' or 'mean'.")


def precompute_scores(
    papers_collection: dict[str, Paper],
    reviewers_collection: dict[str, Reviewer],
) -> dict[str, dict[str, float]]:
    scores: dict[str, dict[str, float]] = {}
    for paper_title in papers_collection:
        scores[paper_title] = {}
        paper_embedding = papers_collection[paper_title].embedding
        for reviewer_name in reviewers_collection:
            reviewer_embeddings = reviewers_collection[reviewer_name].embeddings
            score = sim_pairwise(reviewer_embeddings, paper_embedding)
            scores[paper_title][reviewer_name] = score
        scores[paper_title] = dict(
            sorted(
                scores[paper_title].items(), key=lambda x: x[1], reverse=True
            )
        )
    return scores


def get_score(sol: dict, scores: dict[str, dict[str, float]]) -> float:
    score = 0.0
    for paper_title, reviewer_names in sol.items():
        for name in reviewer_names:
            score += scores[paper_title][name]
    return score


def is_feasible(sol: dict[str, list[str]], constraints: list[Callable]) -> bool:
    return all([constraint(sol) for constraint in constraints])


def is_complete(
    sol: dict[str, list[str]], num_papers: int, reviewers_per_paper: int
) -> bool:
    if not sol or len(sol) != num_papers:
        return False
    return all(
        [len(reviewers) == reviewers_per_paper for reviewers in sol.values()]
    )


def is_leaf(
    sol: dict[str, list[str]],
    constraints: list[Callable],
    num_papers: int,
    reviewers_per_paper: int,
) -> bool:
    return is_feasible(sol, constraints) and is_complete(
        sol, num_papers, reviewers_per_paper
    )


def shuffle_dict(d: dict) -> dict:
    items = list(d.items())
    shuffle(items)
    return dict(items)


def insert_into_queue(q: PriorityQueue, item: PriorityEntry) -> None:
    """
    Inserts an item into the queue by removing lowest
    priority entry when maxsize has been reached
    """
    # If queue does not have maximum size, just add the item.
    if q.maxsize == 0:
        q.put(item)
    else:
        # If there is free space, just add the item
        if len(q.queue) < q.maxsize:
            q.put(item)
        # Otherwise, add the item only if it has higher priority (< in negative)
        else:
            max_queue = max(q.queue)
            if item.priority < max_queue.priority:
                q.queue.remove(max_queue)
                q.put(item)
