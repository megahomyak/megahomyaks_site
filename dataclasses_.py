from dataclasses import dataclass


@dataclass
class ArticleInfo:
    title: str
    html: str


@dataclass
class FileInfo:
    filename: str
    path: str
    creation_time: float
    modification_time: float
