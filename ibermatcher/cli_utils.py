import pandas as pd

from .types import Email, Paper, Reviewer


def split_by(items: str, delimiter: str = ";") -> list[str]:
    return [item.strip() for item in items.split(delimiter)]


def load_reviewers(path: str) -> dict[str, Reviewer]:
    reviewers_df = pd.read_excel(path)
    reviewers_df["categories"] = reviewers_df["categories"].apply(
        lambda x: set(split_by(x, ";"))
    )
    reviewers = reviewers_df.apply(lambda x: Reviewer(**x), axis=1).tolist()
    return {reviewer.full_name: reviewer for reviewer in reviewers}


def load_papers(path: str) -> dict[str, Paper]:
    papers_df = pd.read_excel(path)
    papers_df["authors"] = papers_df["authors"].apply(
        lambda x: set(split_by(x, "\n"))
    )
    papers_df["institutions"] = papers_df["institutions"].apply(
        lambda x: set(split_by(x, "\n"))
    )
    papers_df["countries"] = papers_df["countries"].apply(
        lambda x: set(split_by(x, "\n"))
    )
    papers = papers_df.apply(lambda x: Paper(**x), axis=1).tolist()
    return {paper.title: paper for paper in papers}


def build_emails(
    solution: dict[str, list[str]],
    reviewers_collection: dict[str, Reviewer],
    email_template: str,
) -> list[Email]:
    emails: list[Email] = []
    for paper_title, reviewer_names in solution.items():
        for name in reviewer_names:
            reviewer_email = reviewers_collection[name].email
            email_content = email_template.format(
                reviewer=name, paper=paper_title
            )
            emails.append(Email(to=reviewer_email, content=email_content))
    return emails
