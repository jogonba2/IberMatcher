from dataclasses import dataclass, field
from functools import cache

import numpy as np
from sentence_transformers import SentenceTransformer


@cache
def get_encoder(model_name_or_path: str) -> SentenceTransformer:
    return SentenceTransformer(model_name_or_path)


@dataclass
class Reviewer:
    full_name: str
    institution: str
    country: str
    email: str
    categories: set[str]
    embeddings: np.ndarray = field(init=False)

    def __post_init__(self):
        self.embeddings = get_encoder("all-mpnet-base-v2").encode(
            list(self.categories)
        )


@dataclass
class Paper:
    title: str
    contact: str
    email: str
    authors: set[str]
    institutions: set[str]
    countries: set[str]
    embedding: np.ndarray = field(init=False)
    abstract: str = ""

    def __post_init__(self):
        self.embedding = get_encoder("all-mpnet-base-v2").encode(
            f"{self.title}\n{self.abstract}"
        )


@dataclass(order=True)
class PriorityEntry:
    priority: float
    data: dict = field(compare=False)


@dataclass
class Email:
    to: str
    content: str
