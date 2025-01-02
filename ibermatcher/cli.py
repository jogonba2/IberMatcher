import typer
from typing_extensions import Annotated

from .cli_utils import load_papers, load_reviewers
from .constraints import get_constraints
from .logging import get_logger
from .matchers import get_matcher

_logger = get_logger(__name__)


def match(
    papers_path: Annotated[
        str, typer.Argument(help="Path to the papers pool (excel file)")
    ],
    reviewers_path: Annotated[
        str, typer.Argument(help="Path to the reviewers pool (excel file)")
    ],
    reviewers_per_paper: Annotated[
        int, typer.Argument(help="Number of reviewers per paper")
    ],
    matcher: Annotated[str, typer.Argument(help="Matcher name")],
    constraint_names: list[str] = typer.Option(
        [], help="Names of the constraints"
    ),
):
    # Load pools
    papers_collection = load_papers(papers_path)
    reviewers_collection = load_reviewers(reviewers_path)

    # Get the matcher algorithm
    matcher_fn = get_matcher(matcher)

    # Instantiate constraints
    constraints = get_constraints(
        constraint_names,
        papers_collection,
        reviewers_collection,
        reviewers_per_paper,
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
    typer.run(match)
