from copy import deepcopy
from queue import PriorityQueue
from typing import Callable, Optional

from ..logging import get_logger
from ..types import Paper, PriorityEntry, Reviewer
from .greedy import match_by_greedy
from .utils import (
    get_score,
    insert_into_queue,
    is_feasible,
    is_leaf,
    precompute_scores,
)

_logger = get_logger(__name__)


def get_branches(
    sol: dict[str, list[str]],
    papers_collection: dict[str, Paper],
    reviewers_collection: dict[str, Reviewer],
    constraints: list[Callable],
    reviewers_per_paper: int,
) -> list[dict[str, list[str]]]:
    """
    Branch a partial solution by adding one reviewer to the first uncomplete paper.
    """

    branches = []
    # Get the first paper not appearing in the collection or uncomplete
    current_paper = next(
        (
            paper
            for paper in papers_collection
            if paper not in sol or len(sol[paper]) < reviewers_per_paper
        ),
        None,
    )

    if current_paper is None:
        raise ValueError(
            "There are no papers to be branched."
            "Ensure you pass uncomplete solutions to `get_branches`"
        )

    if current_paper not in sol:
        sol[current_paper] = []

    # Branch the current paper by adding one reviewer
    for reviewer in reviewers_collection:
        branch = deepcopy(sol)
        branch[current_paper].append(reviewer)
        if is_feasible(branch, constraints):
            branches.append(branch)

    return branches


def get_upper_bound(
    sol: dict,
    papers_collection: dict[str, Paper],
    scores: dict[str, dict[str, float]],
    reviewers_per_paper: int,
    constraints: Optional[list[Callable]] = None,
) -> float:
    """
    Compute an upper bound from a partial solution by relaxing the constraints.
    """
    bound = 0.0
    for paper in papers_collection:
        # Compute the accumulated score in the existing partial solution score(p)
        if paper in sol:
            for reviewer in sol[paper]:
                bound += scores[paper][reviewer]
            missing_reviewers = reviewers_per_paper - len(sol[paper])
        else:
            missing_reviewers = reviewers_per_paper

        # If constraints not provided -> compute h(p) by relaxing all the constraints
        if constraints is None:
            if missing_reviewers > 0:
                best_reviewers = list(scores[paper].items())[:missing_reviewers]
                best_scores = [reviewer[1] for reviewer in best_reviewers]
                bound += sum(best_scores)
        else:
            if missing_reviewers > 0:
                best_reviewers = list(scores[paper].items())
                added_reviewers = 0
                paper_not_in_sol = paper not in sol
                if paper_not_in_sol:
                    sol[paper] = []

                # Evaluate all feasible reviewers for the paper
                for reviewer, score in best_reviewers:
                    sol[paper].append(reviewer)
                    if is_feasible(sol, constraints):
                        bound += score
                        added_reviewers += 1
                    sol[paper].remove(reviewer)
                    if added_reviewers >= missing_reviewers:
                        break
                # Clean up if a new paper is added
                if paper_not_in_sol:
                    del sol[paper]

    # Here bound is score(p) + h(p)
    return bound


def match_by_branch_and_bound(
    papers_collection: dict[str, Paper],
    reviewers_collection: dict[str, Reviewer],
    constraints: list[Callable],
    reviewers_per_paper: int,
    return_first_solution: bool = True,
    lower_bound: Optional[float] = None,
    queue_maxsize: int = 0,
    relax_upper_bound: bool = False,
) -> tuple[dict[str, list[str]], float]:
    """
    Finds the optimal alignment by branch and bound, using a greedy
    solution as lower bound if any feasible solution exists.

    This function behaves like beam search when `lower_bound=0.`
    and `queue_max_size > 0`.
    """
    # Precompute scores of reviewers for the papers
    precomputed_scores = precompute_scores(
        papers_collection, reviewers_collection
    )

    # If a lower bound is not provided, use greedy as lower bound.
    if lower_bound is None:
        _logger.info("Lower bound not provided, running greedy search...")
        best_solution, best_score = match_by_greedy(
            papers_collection,
            reviewers_collection,
            constraints,
            reviewers_per_paper,
        )

        if not best_solution:
            # An estimate lower bound based on similarity:
            # 0.4 for all the reviewers in all the papers
            _logger.info(
                "Do not exists a greedy solution, using"
                " the constant similarity heuristic."
            )
            best_score = len(papers_collection) * reviewers_per_paper * 0.4
    else:
        _logger.info(f"Lower bound provided: {lower_bound}")
        best_solution, best_score = {}, lower_bound

    best_score = -best_score  # Negative for maximization
    _logger.info(f"Greedy solution: {best_solution}")
    _logger.info(f"Greedy score: {abs(best_score)}")

    # Prepare the queue and the empty solution
    first_solution: dict[str, list[str]] = {}
    queue: PriorityQueue = PriorityQueue(maxsize=queue_maxsize)
    queue.put(PriorityEntry(0.0, first_solution))

    # Statistics
    pruned_branches = 0
    explored_branches = 0

    while not queue.empty():
        entry = queue.get()
        sol, score = entry.data, entry.priority
        # If the partial solution is not a leaf:
        # 1) Branch the partial solution by adding one reviewer
        #    to the first uncomplete paper
        # 2) Compute the upper bound of each branch
        # 3) Add those whose upper bound is greater than the best solution
        if not is_leaf(
            sol, constraints, len(papers_collection), reviewers_per_paper
        ):
            branches = get_branches(
                sol,
                papers_collection,
                reviewers_collection,
                constraints,
                reviewers_per_paper,
            )
            for branch in branches:
                upper_bound = -get_upper_bound(
                    branch,
                    papers_collection,
                    precomputed_scores,
                    reviewers_per_paper,
                    constraints=constraints if not relax_upper_bound else None,
                )
                branch_score = -get_score(branch, precomputed_scores)
                if upper_bound <= best_score:
                    insert_into_queue(
                        queue, PriorityEntry(branch_score, branch)
                    )
                    explored_branches += 1
                else:
                    pruned_branches += 1
        # Otherwise, if the leaf improves the score,
        # it is our best current solution :)
        else:
            if score < best_score:
                best_solution, best_score = sol, score
                if return_first_solution:
                    _logger.info(f"Pruned branches: {pruned_branches}")
                    _logger.info(f"Explored branches: {explored_branches}")
                    return best_solution, -best_score

    if best_solution is None:
        _logger.error(
            "No solution can be found for this case."
            "Try relaxing the constraints and reviewing your data."
        )
        return None, -1

    _logger.info(f"Pruned branches: {pruned_branches}")
    _logger.info(f"Explored branches: {explored_branches}")
    return best_solution, -best_score
