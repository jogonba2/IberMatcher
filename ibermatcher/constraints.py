""" Feasibility constraints """

from collections import Counter
from functools import partial
from typing import Callable

from .types import Paper, Reviewer


def reviewer_underload(
    sol: dict[str, list[str]], reviewers_per_paper: int, **kwargs
) -> bool:
    """
    All reviewers review <= l papers
    """
    counts = Counter(sum(sol.values(), []))
    if not counts:
        return True
    max_count = counts.most_common(1)[0][1]
    return max_count <= reviewers_per_paper


def reviewer_not_author(
    sol: dict[str, list[str]], papers_collection: dict[str, Paper], **kwargs
) -> bool:
    """
    A reviewer is not an author of the assigned paper
    """
    for paper, reviewers in sol.items():
        authors = set(papers_collection[paper].authors)
        for reviewer in reviewers:
            if reviewer in authors:
                return False
    return True


def unique_reviewers(sol: dict[str, list[str]], **kwargs) -> bool:
    """
    Reviewers must be unique for each paper
    """
    unique = True
    for reviewers in sol.values():
        unique = unique and not len(set(reviewers)) < len(reviewers)
    return unique


def reviewers_from_different_institutions(
    sol: dict[str, list[str]],
    reviewers_collection: dict[str, Reviewer],
    **kwargs,
) -> bool:
    """
    Reviewers of a paper must be from different institutions
    """
    for reviewer_names in sol.values():
        reviewers_institutions = [
            reviewers_collection[name].institution for name in reviewer_names
        ]
        if len(set(reviewers_institutions)) < len(reviewers_institutions):
            return False

    return True


def reviewers_not_authors_institutions(
    sol: dict[str, list[str]],
    papers_collection: dict[str, Paper],
    reviewers_collection: dict[str, Reviewer],
    **kwargs,
) -> bool:
    """
    Reviewers must not be from the authors' institutions
    """
    for paper_title, reviewer_names in sol.items():
        institutions = papers_collection[paper_title].institutions
        for reviewer_name in reviewer_names:
            if reviewers_collection[reviewer_name].institution in institutions:
                return False
    return True


CONSTRAINTS: dict[str, Callable] = {
    "reviewer_underload": reviewer_underload,
    "reviewer_not_author": reviewer_not_author,
    "unique_reviewers": unique_reviewers,
    "reviewers_from_different_institutions": reviewers_from_different_institutions,
    "reviewers_not_authors_institutions": reviewers_not_authors_institutions,
}


def get_constraints(
    names: list[str],
    papers_collection: dict[str, Paper],
    reviewers_collection: dict[str, Reviewer],
    reviewers_per_paper: int,
) -> list[Callable]:

    # If not constraints provided, use all of them
    if not names:
        names = list(CONSTRAINTS.keys())

    constraints: list[Callable] = []
    for name in names:
        if name not in CONSTRAINTS:
            raise ValueError(f"{name} constraint is not supported.")
        constraints.append(
            partial(
                CONSTRAINTS[name],
                papers_collection=papers_collection,
                reviewers_collection=reviewers_collection,
                reviewers_per_paper=reviewers_per_paper,
            )
        )

    return constraints
