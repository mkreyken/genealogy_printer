import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Any, Union


@dataclass
class People:
    people: List[Person]

def id_of(value) -> Optional[str]:
    """Return the ID if value is a Person or a string; otherwise None."""
    if value is None:
        return None
    if isinstance(value, Person):
        return value.id
    return value  # assume it's already a string ID

def ids_of_list(values: Optional[list[Person | str]]) -> List[str]:
    if not values:
        return []
    return [id_ for v in values if (id_ := id_of(v)) is not None]

def ids_of_dict(values: Optional[dict[str, Person | str]]) -> dict[str, str]:
    if not values:
        return {}
    return {k: id_ for k, v in values.items() if (id_ := id_of(v)) is not None}



@dataclass
class Person:
    id: str
    name: str
    sex: str
    mom: Optional[str | Person] = None
    dad: Optional[str | Person] = None
    years: Optional[str] = None
    born_location: Optional[str] = None
    died_location: Optional[str] = None
    cemetery: Optional[str] = None
    married_location: Optional[str] = None
    divorced: Optional[str] = None
    married: Optional[str] = None
    spouse: Optional[List[str | Person]] = None
    children: Optional[List[str | Person]] = None
    notes: Optional[str] = None
    occupation: Optional[str] = None
    vows: Optional[str] = None  # Religious order
    family_nickname: Optional[str] = None
    # person_id, relationship string
    relations: dict[str, str ] = field(default_factory=dict)

    @classmethod
    def random_id(cls, name: str) -> str:
        x = str(random.randint(1, 999999999))
        return name.split()[0] + x

    # --- ID helpers ---
    def mom_id(self) -> Optional[str]:
        return id_of(self.mom)

    def dad_id(self) -> Optional[str]:
        return id_of(self.dad)

    def parent_ids(self) -> List[str]:
        parent_ids = []
        mom_id = self.mom_id()
        dad_id = self.dad_id()
        if mom_id:
            parent_ids.append(mom_id)
        if dad_id is not None:
            parent_ids.append(dad_id)
        return parent_ids

    def spouse_ids(self) -> List[str]:
        return ids_of_list(self.spouse)

    def children_ids(self) -> List[str]:
        return ids_of_list(self.children)

    def is_female(self) -> bool:
        return self.sex.lower() == "f"

    def is_male(self) -> bool:
        return self.sex.lower() == "m"

    @classmethod
    def from_dict(cls, data: dict | None) -> Optional[Person]:

        def convert_person_link(value: Any) -> Optional[Union[str, Person]]:
            if value is None:
                return None
            if isinstance(value, str):
                # spouse: "id123" → wrap the id in list
                return value
            if isinstance(value, dict):
                # spouse: can be singular or list { ... }  → wrap in list
                new_person = cls.from_dict(value)
                if new_person is None:
                    return None
                return new_person
            return None

        def convert_list_link(value: Any) -> Optional[List[Union[str, Person]]]:
            if value is None:
                return None
            if isinstance(value, str):
                # spouse: "id123" → wrap the id in list
                return [value]
            if isinstance(value, dict):
                # spouse: can be singular or list { ... }  → wrap in list
                new_person = cls.from_dict(value)
                if new_person is None:
                    return None
                return [new_person]

            if isinstance(value, list):
                result = []
                for item in value:
                    if isinstance(item, str):
                        result.append(item)
                    elif isinstance(item, dict):
                        result.append(cls.from_dict(item))
                return result
            return None

        if data is None:
            return None
        name = data.get("name")
        if name is None or not isinstance(name, str):
            raise ValueError(f"No Name on {data}")
        if data.get("sex") is None:
            raise ValueError(f" No sex on {data} ")
        person_id = data.get("id", cls.random_id(name))

        d = dict(data)
        # Apply only the special conversions
        d["id"] = person_id
        d["mom"] = convert_person_link(d.get("mom"))
        d["dad"] = convert_person_link(d.get("dad"))
        d["spouse"] = convert_list_link(d.get("spouse"))
        d["children"] = convert_list_link(d.get("children"))

        return cls(**d)

    def get_life_years(self) -> Optional[tuple[Optional[datetime], Optional[datetime]]]:
        if self.years is None:
            return None
        if "-" in self.years:
            b, d = self.years.split('-')
            return self.decode_date(b.strip()), self.decode_date(d.strip())

        b = self.years
        return self.decode_date(b.strip()), None

    @classmethod
    def decode_date(cls, date_as_string: str) -> Optional[datetime]:
        if "." not in date_as_string:
            return None
        d, m, y = date_as_string.split('.')
        if 'x' in d:
            d = 1
        if 'x' in m:
            m = 11
        if 'x' in y:
            y = 2100
        return datetime(int(y), int(m), int(d))
