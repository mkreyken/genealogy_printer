import src.reader.genealogy_reader
from src.reader.relationship_mapper import RelationshipMapper


def print_person(person):
    try:
        for field in person.keys():
            print(field, " = ", person[field])

    except Exception as ex:
        print(person)
        raise ex


def print_person_xml(person):

    try:
        print("<person>")
        for field in person.keys():
            print("<" + field + ">" , person[field] , "</" + field + ">")
        print("</person>")

    except Exception as ex:
        print(person)
        raise ex


def first_in_set(values):
    return next(iter(values))


if __name__ == '__main__':
    #people = input.genealogy_reader.load_people()
    gr = src.reader.genealogy_reader.GenealogyReader()
    people = gr.load_people()
    # input.genealogy_reader.obfuscate_birthday(people)
    rm = RelationshipMapper(people)


    do_person = people["person_id"]
    rm.my_relations(do_person)
    rm.fix_relationship_labels()

    print ("<data>")
    for this_person in people.values():
        print_person_xml(this_person)
    print("</data>")



