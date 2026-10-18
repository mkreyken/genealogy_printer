from typing import Dict, Optional

from models.people import Person
from src.reader.genealogy_reader import GenealogyReader

SELF = "Me"
FATHER = "Father"
MOTHER = "Mother"
GRAND = "Grand "
GREAT = "Great "
BROTHER = "Brother"
SISTER = "Sister"
SPOUSE = "Spouse"

CHILD = "Child"
PARENT = "Parent"
DAUGHTER = "Daughter"
SON = "Son"
AUNT = "Aunt"
UNCLE = "Uncle"
NEPHEW = "Nephew"
NIECE = "Niece"
COUSIN = "Cousin"
ONCE_REMOVED = " Once Removed"
TWICE_REMOVED = " Twice Removed"
THRICE_REMOVED = " Thrice Removed"
FOUR_TIMES_REMOVED = " Four Times Removed"
FIRST = "First "
SECOND = "Second "
THIRD = "Third "
FOURTH = "Fourth "
FIFTH = "Fifth "

# file values
FEMALE = "f"
MALE = "m"

RELATIVE_MAP = {

    SELF + PARENT + PARENT + PARENT + PARENT + PARENT + PARENT + PARENT:
        {FEMALE: GREAT + GREAT + GREAT + GREAT + GREAT + GRAND + MOTHER,
         MALE: GREAT + GREAT + GREAT + GREAT + GREAT + GRAND + FATHER},
    SELF + PARENT + PARENT + PARENT + PARENT + PARENT + PARENT + PARENT + PARENT:
        {FEMALE: GREAT + GREAT + GREAT + GREAT + GREAT + GREAT + GRAND + MOTHER,
         MALE: GREAT + GREAT + GREAT + GREAT + GREAT + GREAT + GRAND + FATHER},

    SELF: {FEMALE: SELF, MALE: SELF},
    SELF + CHILD: {FEMALE: DAUGHTER, MALE: SON},
    SELF + CHILD + CHILD: {FEMALE: GRAND + DAUGHTER, MALE: GRAND + SON},
    SELF + CHILD + CHILD + CHILD: {FEMALE: GREAT + GRAND + DAUGHTER, MALE: GREAT + GRAND + SON},
    SELF + CHILD + CHILD + CHILD + CHILD: {
        FEMALE: GREAT + GREAT + GRAND + DAUGHTER,
        MALE: GREAT + GREAT + GRAND + SON},
    SELF + CHILD + CHILD + CHILD + CHILD + CHILD:
        {FEMALE: THIRD + GREAT + GRAND + DAUGHTER,
         MALE: THIRD + GREAT + GRAND + SON},
    SELF + CHILD + CHILD + CHILD + CHILD + CHILD + CHILD:
        {FEMALE: FOURTH + GREAT + GRAND + DAUGHTER,
         MALE: FOURTH + GREAT + GRAND + SON},

    SELF + PARENT: {FEMALE: MOTHER, MALE: FATHER},
    SELF + PARENT + CHILD: {FEMALE: SISTER, MALE: BROTHER},
    SELF + PARENT + CHILD + CHILD: {FEMALE: NIECE, MALE: NEPHEW},
    SELF + PARENT + CHILD + CHILD + CHILD: {FEMALE: GRAND + NIECE, MALE: GRAND + NEPHEW},
    SELF + PARENT + CHILD + CHILD + CHILD + CHILD: {FEMALE: GREAT + GRAND + NIECE, MALE: GREAT + GRAND + NEPHEW},
    SELF + PARENT + CHILD + CHILD + CHILD + CHILD + CHILD:
        {FEMALE: GREAT + GREAT + GRAND + NIECE,
         MALE: GREAT + GREAT + GRAND + NEPHEW},
    SELF + PARENT + CHILD + CHILD + CHILD + CHILD + CHILD + CHILD:
        {FEMALE: GREAT + GREAT + GREAT + GRAND + NIECE,
         MALE: GREAT + GREAT + GREAT + GRAND + NEPHEW},

    SELF + PARENT + PARENT: {FEMALE: GRAND + MOTHER, MALE: GRAND + FATHER},
    SELF + PARENT + PARENT + CHILD: {FEMALE: AUNT, MALE: UNCLE},
    SELF + PARENT + PARENT + CHILD + CHILD: FIRST + COUSIN,
    SELF + PARENT + PARENT + CHILD + CHILD + CHILD: FIRST + COUSIN + ONCE_REMOVED,
    SELF + PARENT + PARENT + CHILD + CHILD + CHILD + CHILD: FIRST + COUSIN + TWICE_REMOVED,
    SELF + PARENT + PARENT + CHILD + CHILD + CHILD + CHILD + CHILD: FIRST + COUSIN + THRICE_REMOVED,
    SELF + PARENT + PARENT + CHILD + CHILD + CHILD + CHILD + CHILD + CHILD: FIRST + COUSIN + FOUR_TIMES_REMOVED,

    SELF + PARENT + PARENT + PARENT: {FEMALE: GREAT + GRAND + MOTHER, MALE: GREAT + GRAND + FATHER},
    SELF + PARENT + PARENT + PARENT + CHILD: {FEMALE: GREAT + AUNT, MALE: GREAT + UNCLE},
    SELF + PARENT + PARENT + PARENT + CHILD + CHILD: FIRST + COUSIN + ONCE_REMOVED,
    SELF + PARENT + PARENT + PARENT + CHILD + CHILD + CHILD: SECOND + COUSIN,
    SELF + PARENT + PARENT + PARENT + CHILD + CHILD + CHILD + CHILD: SECOND + COUSIN + ONCE_REMOVED,
    SELF + PARENT + PARENT + PARENT + CHILD + CHILD + CHILD + CHILD + CHILD: SECOND + COUSIN + TWICE_REMOVED,
    SELF + PARENT + PARENT + PARENT + CHILD + CHILD + CHILD + CHILD + CHILD + CHILD: SECOND + COUSIN + THRICE_REMOVED,

    SELF + PARENT + PARENT + PARENT + PARENT:
        {FEMALE: GREAT + GREAT + GRAND + MOTHER,
         MALE: GREAT + GREAT + GRAND + FATHER},
    SELF + PARENT + PARENT + PARENT + PARENT + CHILD: {FEMALE: GREAT + GRAND + AUNT, MALE: GREAT + GRAND + UNCLE},
    SELF + PARENT + PARENT + PARENT + PARENT + CHILD + CHILD: FIRST + COUSIN + TWICE_REMOVED,
    SELF + PARENT + PARENT + PARENT + PARENT + CHILD + CHILD + CHILD: SECOND + COUSIN + ONCE_REMOVED,
    SELF + PARENT + PARENT + PARENT + PARENT + CHILD + CHILD + CHILD + CHILD: THIRD + COUSIN,
    SELF + PARENT + PARENT + PARENT + PARENT + CHILD + CHILD + CHILD + CHILD + CHILD: THIRD + COUSIN + ONCE_REMOVED,
    SELF + PARENT + PARENT + PARENT + PARENT + CHILD + CHILD + CHILD + CHILD + CHILD + CHILD: THIRD + COUSIN + TWICE_REMOVED,

    SELF + PARENT + PARENT + PARENT + PARENT + PARENT:
        {FEMALE: THIRD + GREAT + GRAND + MOTHER,
         MALE: THIRD + GREAT + GRAND + FATHER},
    SELF + PARENT + PARENT + PARENT + PARENT + PARENT + CHILD: {FEMALE: GREAT + GREAT + GRAND + AUNT,
                                                                MALE: GREAT + GREAT + GRAND + UNCLE},
    SELF + PARENT + PARENT + PARENT + PARENT + PARENT + CHILD + CHILD: FIRST + COUSIN + THRICE_REMOVED,
    SELF + PARENT + PARENT + PARENT + PARENT + PARENT + CHILD + CHILD + CHILD: SECOND + COUSIN + TWICE_REMOVED,
    SELF + PARENT + PARENT + PARENT + PARENT + PARENT + CHILD + CHILD + CHILD + CHILD: THIRD + COUSIN + ONCE_REMOVED,
    SELF + PARENT + PARENT + PARENT + PARENT + PARENT + CHILD + CHILD + CHILD + CHILD + CHILD: FOURTH + COUSIN,
    SELF + PARENT + PARENT + PARENT + PARENT + PARENT + CHILD + CHILD + CHILD + CHILD + CHILD + CHILD: FOURTH + COUSIN + ONCE_REMOVED,

    SELF + PARENT + PARENT + PARENT + PARENT + PARENT + PARENT:
        {FEMALE: FOURTH + GREAT + GRAND + MOTHER,
         MALE: FOURTH + GREAT + GRAND + FATHER},

    SELF + PARENT + PARENT + PARENT + PARENT + PARENT + PARENT + CHILD: {FEMALE: THIRD + GREAT + GRAND + AUNT,
                                                                         MALE: THIRD + GREAT + GRAND + UNCLE},
    SELF + PARENT + PARENT + PARENT + PARENT + PARENT + PARENT + CHILD + CHILD: FIRST + COUSIN + FOUR_TIMES_REMOVED,
    SELF + PARENT + PARENT + PARENT + PARENT + PARENT + PARENT + CHILD + CHILD + CHILD: SECOND + COUSIN + THRICE_REMOVED,
    SELF + PARENT + PARENT + PARENT + PARENT + PARENT + PARENT + CHILD + CHILD + CHILD + CHILD: THIRD + COUSIN + TWICE_REMOVED,
    SELF + PARENT + PARENT + PARENT + PARENT + PARENT + PARENT + CHILD + CHILD + CHILD + CHILD + CHILD: FOURTH + COUSIN + ONCE_REMOVED,
    SELF + PARENT + PARENT + PARENT + PARENT + PARENT + PARENT + CHILD + CHILD + CHILD + CHILD + CHILD + CHILD: FIFTH + COUSIN,

    SELF + PARENT + PARENT + CHILD + SPOUSE: {FEMALE: AUNT, MALE: UNCLE},
    SELF + SPOUSE + PARENT: {FEMALE: "Mother In Law", MALE: "Father In Law"},
    SELF + SPOUSE + PARENT + CHILD: {FEMALE: "Sister In Law", MALE: "Brother In Law"},
    SELF + SPOUSE + PARENT + CHILD + CHILD: {FEMALE: NIECE, MALE: NEPHEW}
    # MeSpouseParentParentChildSpouse Aunt in Law? Uncle In Law
}


def convert_relationships(person) -> dict[str, str]:
    try:
        if not person.relations:
            return {}

        result = {}
        relationship = person.relations
        sex = person.sex

        for other_id in relationship.keys():
            value = relationship[other_id]
            if RELATIVE_MAP.get(value):
                value = RELATIVE_MAP[value]
                if type(value) is dict:
                    value = value[sex]
            result[other_id] = value
        return result
    except Exception as ex:
        print(person)
        raise ex


class RelationshipMapper:
    people: dict[str, Person]
    queue: list[Person]

    def __init__(self, people: Dict[str, Person]):
        self.people = people
        self.queue = []

    def __add_to_queue(self, person: Person):
        self.queue.append(person)

    def __next_in_queue(self) -> Optional[Person]:
        if len(self.queue) == 0:
            return None
        return self.queue.pop()

    def __add_me(self, person: Person, other_id):
        relation = SELF
        if not person.relations:
            person.relations = dict()
        if person.relations.get(other_id):
            return
        person.relations[other_id] = relation
        self.__add_to_queue(person)

    def __add_parent(self, what: str, person: Person, other_id):
        relation = what + PARENT
        if not person.relations:
            person.relations = dict()
        if person.relations.get(other_id):
            return
        person.relations[other_id] = relation
        self.__add_to_queue(person)

    def __add_spouse(self, what: str, person: Person, other_id: str):
        relation = what + SPOUSE
        if not person.relations:
            person.relations = dict()
        if person.relations.get(other_id):
            return
        person.relations[other_id] = relation
        self.__add_to_queue(person)

    def __add_child(self, what: str, person: Person, other_id: str):
        relation = what + CHILD
        if not person.relations:
            person.relations = dict()
        if person.relations.get(other_id):
            return
        person.relations[other_id] = relation
        self.__add_to_queue(person)

    # Add a relationship of person to other_id i.e. Person is the Father of other_id
    # then if this is a new relationship, then use this person to distribute that relationship
    def __add_relations(self, person: Person, other_id: str):
        try:
            relation = person.relations[other_id]
            parent_ids = person.parent_ids()
            if parent_ids:
                for parent_id in parent_ids:
                    parent = self.people[parent_id]
                    self.__add_parent(relation, parent, other_id)

            for spouse_id in person.spouse_ids():
                self.__add_spouse(relation, self.people[spouse_id], other_id)

            for child_id in person.children_ids():
                child = self.people[child_id]
                self.__add_child(relation, child, other_id)
        except Exception as ex:
            print("ex:" + str(person))
            raise ex

    # We only add direct parents, and direct children here ,
    # not parents of children related (un related people), as those require qualifiers
    # i.e. Grand Father of My Grand Niece.
    def my_relations(self, person: Person) -> None:
        other_id = person.id
        self.__add_me(person, other_id)
        while True:
            person_next = self.__next_in_queue()
            if not person_next:
                return
            self.__add_relations(person_next, other_id)

    def fix_relationship_labels(self) -> None:
        for person in self.people.values():
            person.relations = convert_relationships(person)


def sort_key_by_id(person: Person):
    return person.id.lower()


def print_list_by_id(people: Dict[str, Person], sort_key_func):
    peoples = []
    for person in people.values():
        peoples.append(person)

    peoples.sort(key=sort_key_func)
    for person in peoples:
        print(person.id + ":" + str(person))


if __name__ == '__main__':
    gr = GenealogyReader()
    these_people = gr.load_people()
    rm = RelationshipMapper(these_people)
    rm.fix_relationship_labels()
    print_list_by_id(these_people, sort_key_by_id)
