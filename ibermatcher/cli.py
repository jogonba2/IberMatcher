from typer import run

from .cli_utils import load_papers, load_reviewers
from .constraints import get_all_constraints
from .logging import get_logger
from .matchers import get_matcher

_logger = get_logger(__name__)


def match(
    papers_path: str,
    reviewers_path: str,
    reviewers_per_paper: int,
    matcher: str,
):

    # Load pools
    papers_collection = load_papers(papers_path)
    reviewers_collection = load_reviewers(reviewers_path)

    # Get the matcher algorithm
    matcher_fn = get_matcher(matcher)

    # Instantiate constraints
    constraints = get_all_constraints(
        papers_collection, reviewers_collection, reviewers_per_paper
    )

    # Run the matcher
    solution, score = matcher_fn(
        papers_collection,
        reviewers_collection,
        constraints,
        reviewers_per_paper,
    )
    _logger.info(f"Solution: {solution}")
    _logger.info(f"Score: {score}")


if __name__ == "__main__":
    run(match)
