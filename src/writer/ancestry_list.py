import src.reader.genealogy_reader
from src import reader
from src.reader.relationship_mapper import RelationshipMapper


def print_tree(people_list, person, fields_to_walk, fields_to_print, level=0):
    try:
        next_person = person
        output = next_person[reader.PERSON_NAME] + " -> "
        list_related = []
        for field in fields_to_walk:
            if field in next_person:
                lookup = next_person[field]
                if type(lookup) is set:
                    for each in lookup:
                        list_related.append(each)
                else:
                     list_related.append(lookup)

        output_list = []
        for field in fields_to_print:
            if field in next_person:
                lookup = next_person[field]
                if field == reader.PERSON_SPOUSES:
                    for spouse_id in lookup:
                        output_list.append(" Spouse: " + people_list[spouse_id][reader.PERSON_NAME] + " " + people_list[spouse_id].get(
                            reader.PERSON_YEARS, "(Bday ?)"))
                elif field == reader.RELATIONS:
                    for other_id in lookup.keys():
                        output_list.append(lookup[other_id] + " of " + people_list[other_id][reader.PERSON_NAME])
                else:
                    output_list.append(field + " : " + str(lookup))

        output += " | ".join(output_list)
        print(" " * (level * 3) + output)
        for lookup in list_related:
            for item in lookup:
                print_tree(people_list, people_list[item], fields_to_walk, fields_to_print, level + 1)

    except Exception as ex:
        print(person)
        raise ex


def first_in_set(values):
    return next(iter(values))


if __name__ == '__main__':
    gr = src.reader.genealogy_reader.GenealogyReader()
    people = gr.load_people()
    # input.genealogy_reader.obfuscate_birthday(people)
    rm = RelationshipMapper(people)
    do_person = people["person_id"]
    rm.my_relations(do_person)

    rm.fix_relationship_labels()

    print_tree(people, do_person, [reader.PERSON_PARENTS], [reader.PERSON_YEARS])
    for parent_id in do_person[reader.PERSON_PARENTS]:
        parent = people[parent_id]
        if parent[reader.PERSON_SEX] == reader.PERSON_MALE:
            print_tree(people, parent, [reader.PERSON_CHILDREN], [reader.PERSON_YEARS, reader.PERSON_SPOUSES, reader.RELATIONS])



