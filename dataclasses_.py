from dataclasses import dataclass


@dataclass
class ArticleInfo:
    path: str
    title: str


@dataclass
class ArticlePathInfo:
    path: str
    filename: str
