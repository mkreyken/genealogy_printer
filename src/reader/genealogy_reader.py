import json
import os
from typing import Any, Dict, Optional, List

from models.people import People, Person, id_of
from src.utils.filesystem import get_data_directory


class GenealogyReader:
    people: Dict[str, Person]

    def __init__(self):
        self.people = {}

    # ensure that all children point to parents and all parents point to children
    # raw names are no longer permitted, so at this point all people id's must have been created
    def fix_relations(self) -> None:
        for person in self.people.copy().values():

            parent_ids = person.parent_ids()
            new_parent_ids = []
            for parent_id in parent_ids:
                if self.people.get(parent_id):
                    new_parent_ids.append(parent_id)
                    parent = self.people[parent_id]
                    children = person.children
                    if children is None:
                        children = []
                    person_id = person.id
                    if person_id not in children:
                        children.append(person_id)
                        parent.children = children
                else:
                    raise ValueError(f"missing connector:{person.id}->{parent_id}")

            # if I have spouses, are spouse all valid
            spouse_ids = person.spouse_ids()
            for spouse_id in spouse_ids:
                if self.people.get(spouse_id):
                    spouse = self.people.get(spouse_id)
                    if spouse is None:
                        raise ValueError(f" can not find spouse:{spouse_id}")
                    if spouse.spouse is None:
                        spouse.spouse = [person.id]
                    elif spouse_id not in spouse.spouse:
                        spouse.spouse.append(person.id)

    # if I have dad, and no mom, and dad has 1 spouse then warning and fix
    # if I have mom, and no dad, and dad has 1 spouse then warning and fix
    # if I have dad, and no mom, and dad has >1 spouse then error
    # if I have mom, and no dad, and dad has >11 spouse then error
    def fix_single_parent(self) -> None:
        for person in self.people.values():
            if person.dad is not None and person.mom is not None:
                continue
            dad_id = person.dad_id()
            mom_id = person.mom_id()

            if dad_id is not None:
                dad = self.people.get(dad_id)
                if dad is None:
                    raise Exception(f"can not find dad:{dad_id}")
                if dad.spouse is not None:
                    print(f"No Mom/spouse:{dad.name}, {dad.years or ''}")
                else:
                    raise Exception(f"can opps spouse:{dad_id}")

            if mom_id is not None:
                mom = self.people.get(mom_id)
                if mom is None:
                    raise Exception(f"can not find mom:{mom_id}")
                if mom.spouse is not None:
                    print(f"No Dad/spouse:{mom.name}, {mom.years or ''}")
                else:
                    raise Exception(f"can oops spouse:{mom_id}")

    @classmethod
    def _collect(cls, person: str | Person, out: dict[str, Person]) -> None:
        """Recursively collect Person objects into `out` dict and fix back-relations."""
        if person is None or not isinstance(person, Person):
            return

        pid = person.id
        if pid in out:
            return

        out[pid] = person

        # --- Handle mom/dad reverse links ---
        if isinstance(person.mom, Person):
            # child -> mom
            cls._collect(person.mom, out)
            # mom -> child (append if missing)
            if person not in (person.mom.children or []):
                person.mom.children = (person.mom.children or []) + [person]

        if isinstance(person.dad, Person):
            cls._collect(person.dad, out)
            if person not in (person.dad.children or []):
                person.dad.children = (person.dad.children or []) + [person]

        # --- Handle spouse reverse links ---
        if person.spouse:
            for s in person.spouse:
                if isinstance(s, Person):
                    cls._collect(s, out)
                    # spouse -> person (append if missing)
                    if person not in (s.spouse or []):
                        s.spouse = (s.spouse or []) + [person]

        # --- Handle children reverse links ---
        if person.children:
            for c in person.children:
                if isinstance(c, Person):
                    cls._collect(c, out)

                    # child -> parent (only if not already set)
                    # We do NOT guess mom/dad; we only add if empty.
                    if c.mom is None and person.is_female():
                        c.mom = person
                    elif c.dad is None and person.is_male:
                        c.dad = person

    @classmethod
    def _replace_embedded(cls, person: Person) -> None:
        """Rewrite embedded Person objects into IDs only. Should only be done after flattening the people."""
        person.mom = id_of(person.mom)
        person.dad = id_of(person.dad)
        person.spouse = person.spouse_ids()
        person.children = person.children_ids()

    def flatten_people(self) -> None:
        """Flatten nested people into a dict and rewrite embedded references."""
        flat = {}

        # 1. Collect all people recursively
        for p in self.people.values():
            self._collect(p, flat)

        # 2. Rewrite embedded Person objects into IDs
        for p in flat.values():
            self._replace_embedded(p)

        # 3. Replace the original list with a flat dict
        self.people = flat

    @classmethod
    def convert_from_json(cls, json_data: Dict[str, Any]) -> People:
        people_raw = json_data.get("people", [])
        people: List[Person] = []
        for p in people_raw:
            person = Person.from_dict(p)
            if person is None:
                raise ValueError(f"on {people_raw}")
            people.append(person)
        return People(people=people)

    # load from this list of files all people and build a dict<person_id, person> from that data
    def load_people(self, files: Optional[List[str]] = None) -> dict[str, Person]:
        data_dir = get_data_directory().absolute()

        if not files:
            files = os.listdir(data_dir)
        for file in files:
            if file.lower().endswith(".json"):
                full_file_name = os.path.join(data_dir, file)
                if os.path.isfile(full_file_name):
                    print(file)
                    with open(full_file_name, encoding='utf-8') as f:
                        data = json.load(f)
                        results = self.convert_from_json(data)
                        for person in results.people:
                            self.people[person.id] = person

        self.flatten_people()
        self.fix_relations()
        self.fix_single_parent()

        # need 2 passes
        self.fix_relations()

        return self.people


if __name__ == '__main__':
    gr = GenealogyReader()
    people2 = gr.load_people()
