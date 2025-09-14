from pydantic import BaseModel
from datetime import date
from typing import List

class Paper(BaseModel):
    pmid: str
    title: str
    abstract: str
    summary: str
    pubdate: date

    class Config:
        json_encoders = {
            date: lambda v: v.isoformat()
        }

class SearchResult(BaseModel):
    drug: str
    papers: List[Paper]

