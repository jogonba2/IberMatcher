# flake8: noqa
from .beam_search import *
from .branch_and_bound import *
from .greedy import *

MATCHERS: dict[str, Callable] = {
    "branch_and_bound": match_by_branch_and_bound,
    "greedy": match_by_greedy,
    "beam_search": match_by_beam_search,
}


def get_matcher(matcher: str) -> Callable:
    if matcher in MATCHERS:
        return MATCHERS[matcher]
    else:
        raise ValueError(f"{matcher} matcher is not implemented.")
