import json
import os
import random
from datetime import datetime
from typing import Any, Dict, Optional, Union, List
from ordered_set import OrderedSet

from models.people import PersonAsJson, PeopleAsJson, Person
from src import reader
from src.utils.filesystem import get_data_directory


class GenealogyReader:

    def __init__(self):
        # self.people : Dict[str,Person] = {}
        self.people : Dict[str,Any] = {}

    @classmethod
    def random_id(cls, person) -> str:
        x = str(random.randint(1, 999999999))
        if reader.PERSON_NAME in person:
            return person[reader.PERSON_NAME].split()[0] + x
        else:
            return "Unknown" + x

    @classmethod
    def decode_date(cls, date_as_string):
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

    @classmethod
    def decode_years(cls, person):
        if reader.PERSON_YEARS not in person:
            return
        years = person[reader.PERSON_YEARS]
        try:
            if "-" in years:
                person[reader.PERSON_BIRTH_DATE], person[reader.PERSON_DEAD_DATE] = [cls.decode_date(x.strip()) for x in
                                                                                     years.split('-')]
            else:
                person[reader.PERSON_BIRTH_DATE] = cls.decode_date(years)

            if reader.PERSON_DEAD_DATE in person and not person[reader.PERSON_DEAD_DATE]:
                person.discard(reader.PERSON_DEAD_DATE)
            if reader.PERSON_BIRTH_DATE in person and not person[reader.PERSON_BIRTH_DATE]:
                person.discard(reader.PERSON_BIRTH_DATE)
        except ValueError:
            print("Exception with year:" + years)

    # given a person as dict, adds an id if none is present
    # returns the id if we already know them, and the data should self merge
    # if you need someone to appear twice, manually assign them numbers that match.
    @classmethod
    def fixup_person_id(cls, person=None):
        if reader.PERSON_ID in person:
            return person[reader.PERSON_ID]

        person_id = cls.random_id(person)
        person[reader.PERSON_ID] = person_id
        return person_id

    @classmethod
    def obfuscate_birthday(cls, people_to_obfuscate):
        for person in people_to_obfuscate.values():
            if person.get(reader.PERSON_YEARS):
                if "-" not in person[reader.PERSON_YEARS] and "x" not in person[reader.PERSON_YEARS]:
                    date_it = person[reader.PERSON_YEARS].split(".")
                    date_it[0] = "-"
                    person[reader.PERSON_YEARS] = ".".join(date_it)

    def create_new_person(self, name=None, sex=None):
        person = {reader.PERSON_NAME: name, reader.PERSON_SEX: sex}
        person_id = self.fixup_person_id(person)
        self.people[person_id] = person
        return person_id

    # changes people
    # returns a set of names, or a single name
    # spouses and children can be lists or individuals. returns set
    # mom and dad relations cannot be set this way since they are a one to many, and are only for convenience
    # persons must be a list
    def load_sub_persons(self, persons, relationship=None, list_ids=None):
        ids = OrderedSet()
        for person in persons:
            if type(person) is dict:
                if list_ids:
                    person[relationship] = list_ids

                ids.add(self.load_person(person))
            else:
                ids.add(person)
        return ids

    # person must be a dict
    def load_sub_person(self, person,
                        sex=None, relationship1=None, parent1_id=None, relationship2=None, parent2_id=None):
        if not person.get(reader.PERSON_SEX):
            person[reader.PERSON_SEX] = sex
        if parent1_id:
            person[relationship1] = parent1_id
        if parent2_id:
            person[relationship2] = parent2_id
        return self.load_person(person)

    # spouse is NONE or List upon converting
    # in a drop list, the first spouse is the spouse of children, use other form if not
    def load_spouses(self, person):
        spouse_id = None
        person_id = person[reader.PERSON_ID]

        if reader.PERSON_SPOUSES in person:
            me_as_spouse_ids = OrderedSet()
            me_as_spouse_ids.add(person_id)
            if type(person[reader.PERSON_SPOUSES]) is dict:
                result_ids = [self.load_sub_person(person[reader.PERSON_SPOUSES], None,
                                                   reader.PERSON_SPOUSES, me_as_spouse_ids)]
            elif type(person[reader.PERSON_SPOUSES]) is list:
                result_ids = self.load_sub_persons(person[reader.PERSON_SPOUSES],
                                                   reader.PERSON_SPOUSES, me_as_spouse_ids)
            elif type(person[reader.PERSON_SPOUSES]) is OrderedSet:
                result_ids = person[reader.PERSON_SPOUSES]
            else:
                result_list = person[reader.PERSON_SPOUSES].split(",")
                result_ids = set(result_list)
            person[reader.PERSON_SPOUSES] = result_ids
            spouse_id = list(result_ids)[0]
        return spouse_id

    def load_children(self, person, person_id, spouse_id):
        # children are NONE or List upon converting
        if reader.PERSON_CHILDREN in person:
            parent_ids = OrderedSet()
            parent_ids.add(person_id)
            if spouse_id:
                parent_ids.add(spouse_id)

            if type(person[reader.PERSON_CHILDREN]) is dict:
                result_ids = [self.load_sub_person(person[reader.PERSON_CHILDREN], None,
                                                   reader.PERSON_PARENTS, parent_ids)]
            elif type(person[reader.PERSON_CHILDREN]) is list:
                result_ids = self.load_sub_persons(person[reader.PERSON_CHILDREN],
                                                   reader.PERSON_PARENTS, parent_ids)
            else:
                result_ids = person[reader.PERSON_CHILDREN].split(",")
            person[reader.PERSON_CHILDREN] = result_ids

    def add_parent(self, person, relationship, sex):
        if relationship in person:
            if type(person[relationship]) is list:
                raise Exception("Cannot have more than one mom:" + person[relationship])
            if reader.PERSON_PARENTS in person:
                parent_ids = person[reader.PERSON_PARENTS]
            else:
                parent_ids = OrderedSet()
            if type(person[relationship]) is dict:
                result_id = self.load_sub_person(person[relationship], sex=sex)
                person[relationship] = result_id
                parent_ids.add(result_id)
            else:
                parent_ids.add(person[relationship])
            person[reader.PERSON_PARENTS] = parent_ids

    # recursive
    # changes people
    def load_person(self, person):
        try:
            person_id = self.fixup_person_id(person)
            # ID already exists/ so this is a cross file match of data in both data sets
            if person_id in self.people:
                spouse_id = self.load_spouses(person)
                if spouse_id:
                    self.load_children(person, person_id, spouse_id)
                self.add_parent(person, reader.PERSON_MOM, reader.PERSON_FEMALE)
                self.add_parent(person, reader.PERSON_DAD, reader.PERSON_MALE)
            else:
                self.people[person_id] = person
                spouse_id = self.load_spouses(person)
                self.load_children(person, person_id, spouse_id)
                self.add_parent(person, reader.PERSON_MOM, reader.PERSON_FEMALE)
                self.add_parent(person, reader.PERSON_DAD, reader.PERSON_MALE)
            return person_id
        except Exception as ex:
            print(person)
            raise ex

    # convert to OrderedSet
    def fix_set_of_people(self, set_of_people):
        if type(set_of_people) is OrderedSet:
            return set_of_people

        fixed_list = OrderedSet()
        for person_id in set_of_people:
            if person_id not in self.people.keys():
                raise Exception("missing connector:" + person_id)
                # new_set.add(self.create_new_person(name=person_id, sex=sex))
            fixed_list.add(person_id)
        return fixed_list

    # ensure that all children point to parents and all parents point to children
    # raw names are no longer permitted, so at this point all people id's must have been created
    # converts set to OrderedSet
    def fix_relations(self):
        for person in self.people.copy().values():
            try:
                parent_ids = person.get(reader.PERSON_PARENTS)
                # If I have parents, then Parents should have me as a Child
                if parent_ids:
                    new_parent_ids = OrderedSet()
                    for parent_id in parent_ids:
                        if self.people.get(parent_id):
                            new_parent_ids.add(parent_id)
                            parent = self.people[parent_id]
                            if not parent.get(reader.PERSON_CHILDREN):
                                parent[reader.PERSON_CHILDREN] = OrderedSet()
                            person_id = person[reader.PERSON_ID]
                            if person_id not in parent[reader.PERSON_CHILDREN]:
                                parent[reader.PERSON_CHILDREN].add(person_id)
                        else:
                            raise Exception("missing connector:" + str(person[reader.PERSON_ID]) + "->" + str(parent_id))
                            # new_person_id = self.create_new_person(name=parent_id, sex=sex)
                            # new_parent_ids.add(new_person_id)

                # if I have spouses, are spouse all valid
                if reader.PERSON_SPOUSES in person:
                    person[reader.PERSON_SPOUSES] = self.fix_set_of_people(person[reader.PERSON_SPOUSES])

                # if I have children, are children all valid
                if reader.PERSON_CHILDREN in person:
                    person[reader.PERSON_CHILDREN] = self.fix_set_of_people(person[reader.PERSON_CHILDREN])
            except Exception as ex:
                print(person)
                raise ex

    def check_sex(self):
        for person in self.people.values():
            try:
                if reader.PERSON_SEX not in person:
                    raise Exception("missing sex:" + str(person[reader.PERSON_ID]))
            except Exception as ex:
                print(person)
                raise ex

    # if I have dad, and no mom, and dad has 1 spouse then warning and fix
    # if I have mom, and no dad, and dad has 1 spouse then warning and fix
    # if I have dad, and no mom, and dad has >1 spouse then error
    # if I have mom, and no dad, and dad has >11 spouse then error
    def fix_single_parent(self):
        for person in self.people.values():
            try:
                if person.get(reader.PERSON_PARENTS) and len(person[reader.PERSON_PARENTS]) == 1:
                    dad: dict[str, Any] | None = None
                    mom: dict[str, Any] | None = None
                    for parent_id in person[reader.PERSON_PARENTS]:
                        if self.people[parent_id][reader.PERSON_SEX] == "m":
                            dad = self.people[parent_id]
                        elif self.people[parent_id][reader.PERSON_SEX] == "f":
                            mom = self.people[parent_id]
                        else:
                            raise Exception("missing sex:" + str(person[reader.PERSON_ID]))
                    if not dad and not mom:
                        raise RuntimeError("No Parents")
                    elif mom and not dad and reader.PERSON_SPOUSES in mom and len(mom.get(reader.PERSON_SPOUSES, [])) > 0:
                        if len(mom[reader.PERSON_SPOUSES]) > 1:
                            raise Exception("too many spouses mom:" + str(person[reader.PERSON_ID]))
                        person[reader.PERSON_PARENTS].add(mom[reader.PERSON_SPOUSES][0])
                    elif dad and not mom and reader.PERSON_SPOUSES in dad and len(dad.get(reader.PERSON_SPOUSES, [])) > 0:
                        if len(dad[reader.PERSON_SPOUSES]) > 1:
                            raise Exception("too many spouses dad:" + str(person[reader.PERSON_ID]))
                        person[reader.PERSON_PARENTS].add(dad[reader.PERSON_SPOUSES][0])

            except Exception as ex:
                print(person)
                raise ex


    def convert_to_dict(self,people:PeopleAsJson) -> None:
        pass

    def load_person2(self, data: Dict[str, Any]) -> PersonAsJson:
        """Convert a dict into a PersonAsJson, recursively."""

        def convert_maybe_person(value: Any) -> Optional[Union[str, PersonAsJson]]:
            if value is None:
                return None
            if isinstance(value, str):
                return value
            if isinstance(value, dict):
                return self.load_person(value)
            return None

        def convert_list(value: Any) -> Optional[List[Union[str, PersonAsJson]]]:
            if value is None:
                return None
            if isinstance(value, dict):
                # spouse: { ... }  → wrap in list
                return [self.load_person(value)]
            if isinstance(value, str):
                # spouse: "id123" → wrap in list
                return [value]
            if isinstance(value, list):
                result = []
                for item in value:
                    if isinstance(item, str):
                        result.append(item)
                    elif isinstance(item, dict):
                        result.append(self.load_person(item))
                return result
            return None

        return PersonAsJson(
            id=data.get("id"),
            name=data.get("name", ""),
            sex=data.get("sex"),
            mom=convert_maybe_person(data.get("mom")),
            dad=convert_maybe_person(data.get("dad")),
            years=data.get("years"),
            born_location=data.get("born_location"),
            died_location=data.get("died_location"),
            married_location=data.get("married_location"),
            divorced=data.get("divorced"),
            married=data.get("married"),
            spouse=convert_list(data.get("spouse")),
            children=convert_list(data.get("children")),
            notes=data.get("notes"),
        )


    def convert_from_json(self, json_data: Dict[str, Any]) -> PeopleAsJson:
        """Convert the top-level dict into PeopleAsJson."""
        people_raw = json_data.get(reader.PEOPLE_GROUP, [])
        people = [self.load_person(p) for p in people_raw]
        return PeopleAsJson(people=people)

    # load from this list of files all people and build a dict<person_id, person> from that data
    def load_people(self, files=None):
        data_dir = get_data_directory().absolute()

        if not files:
            files = os.listdir(data_dir)
        results = None
        for file in files:
            if file.lower().endswith(".json"):
                full_file_name = os.path.join(data_dir, file)
                if os.path.isfile(full_file_name):
                    print(file)
                    with open(full_file_name, encoding='utf-8') as f:
                        data = json.load(f)
                        # ** is enumerate all in list
                        # people = {**people, **data}
                    for person in data[reader.PEOPLE_GROUP]:
                        self.load_person(person)


                    #results = self.convert_from_json(data)
        #assert results is not None
        #self.convert_to_dict(results)
        self.check_sex()
        self.fix_relations()
        self.fix_single_parent()

        # need 2 passes
        self.fix_relations()

        return self.people


if __name__ == '__main__':
    gr = GenealogyReader()
    people = gr.load_people()
