from typing import Callable

from ..types import Paper, Reviewer
from .branch_and_bound import match_by_branch_and_bound


def match_by_beam_search(
    papers_collection: dict[str, Paper],
    reviewers_collection: dict[str, Reviewer],
    constraints: list[Callable],
    reviewers_per_paper: int,
    beam_size: int,
    return_first_solution: bool = True,
):
    return match_by_branch_and_bound(
        papers_collection,
        reviewers_collection,
        constraints,
        reviewers_per_paper,
        lower_bound=0.0,
        queue_maxsize=beam_size,
        return_first_solution=return_first_solution,
    )
