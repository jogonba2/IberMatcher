from copy import deepcopy
from queue import PriorityQueue
from typing import Callable

from ..logging import get_logger
from ..types import Paper, Reviewer
from .utils import get_score, is_feasible, precompute_scores, shuffle_dict

_logger = get_logger(__name__)


def _get_greedy_solution(
    papers_collection: dict[str, Paper],
    reviewers_collection: dict[str, Reviewer],
    constraints: list[Callable],
    scores: dict[str, dict[str, float]],
    reviewers_per_paper: int,
) -> dict[str, list[str]]:
    sol: dict[str, list[str]] = {}
    for paper in papers_collection:
        sol[paper] = []
        queue: PriorityQueue = PriorityQueue()

        # Evaluate all feasible reviewers for the paper
        for reviewer in reviewers_collection:
            sol[paper].append(reviewer)
            if is_feasible(sol, constraints):
                score = scores[paper][reviewer]
                queue.put(
                    (-score, reviewer)
                )  # Negative score for max-priority queue behavior
            sol[paper].remove(reviewer)

        # Ensure enough feasible reviewers are available
        if len(queue.queue) < reviewers_per_paper:
            raise ValueError(
                f"There are not {reviewers_per_paper} reviewers to make a feasible solution for "
                f"the paper {paper}. Try relaxing your constraints."
            )

        # Assign the top `l` reviewers based on score
        for _ in range(reviewers_per_paper):
            sol[paper].append(queue.get()[1])

    return sol


def match_by_greedy(
    papers_collection: dict[str, Paper],
    reviewers_collection: dict[str, Reviewer],
    constraints: list[Callable],
    reviewers_per_paper: int,
    iters: int = 5000,
) -> tuple[dict[str, list[str]], float]:
    """
    Wraps _match_by_greedy to iter `iters` times with different orders.
    """
    solutions = []
    scores = precompute_scores(papers_collection, reviewers_collection)
    for _ in range(iters):
        try:
            solution = _get_greedy_solution(
                papers_collection,
                reviewers_collection,
                constraints,
                scores,
                reviewers_per_paper,
            )
            score = get_score(solution, scores)
            solutions.append((solution, score))
        except ValueError:
            papers_collection = shuffle_dict(deepcopy(papers_collection))
            reviewers_collection = shuffle_dict(deepcopy(reviewers_collection))

    if not solutions:
        _logger.error(
            f"No greedy solution found after {iters} iterations. Try relaxing your constraints."
        )

        return {}, 0.0
    else:
        return sorted(solutions, key=lambda x: x[1], reverse=True)[0]
