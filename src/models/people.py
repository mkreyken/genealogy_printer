from dataclasses import dataclass
from typing import Optional, List


@dataclass
class PersonAsJson:
    id: Optional[str]
    name: str
    sex: Optional[str]
    mom: Optional[str | PersonAsJson]
    dad: Optional[str | PersonAsJson]
    years: Optional[str]
    born_location: Optional[str]
    died_location: Optional[str]
    married_location: Optional[str]
    divorced: Optional[str]
    married: Optional[str]
    spouse: Optional[List[str | PersonAsJson]]
    children: Optional[List[str | PersonAsJson]]
    notes: Optional[str]
    relations : Optional[dict[str, str | PersonAsJson]]

@dataclass
class PeopleAsJson:
    people: List[PersonAsJson]

@dataclass
class Person:
    id: str
    name: str
    sex: Optional[str]
    mom: Optional[str | Person]
    dad: Optional[str | Person]
    birth_date: Optional[str]
    death_date: Optional[str]
    born_location: Optional[str]
    died_location: Optional[str]
    married_location: Optional[str]
    divorced: Optional[str]
    married: Optional[str]
    spouse: Optional[List[str | Person]]
    children: Optional[List[str | Person]]
    notes: Optional[str]

