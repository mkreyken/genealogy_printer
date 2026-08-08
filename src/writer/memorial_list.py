import src
from src import reader
from src.reader import genealogy_reader,relationship_mapper


# given a person, returns the sort key for the month and day for calendar sorting of death
def sort_key_by_month_and_day(person):
    return format(person[reader.PERSON_DEAD_DATE].month, '02d') \
           + format(person[reader.PERSON_DEAD_DATE].day, '02d') + person[reader.PERSON_NAME]


# people : a dict<person_id, person>
# sort_key_func a function that given a person returns a key to use for standard sorting
def print_expired_sorted_month_date(people, sort_key_func, other_id):
    people_dead = []
    for person in people.values():
        if person[reader.RELATIONS].get(other_id) \
                and not person[reader.RELATIONS][other_id].startswith(src.reader.relationship_mapper.SELF):
            genealogy_reader.GenealogyReader.decode_years(person)
            if reader.PERSON_DEAD_DATE in person:
                people_dead.append(person)

    people_dead.sort(key=sort_key_func)
    for person in people_dead:
        output = format(person[reader.PERSON_DEAD_DATE].month, '02d') + "-" \
                 + format(person[reader.PERSON_DEAD_DATE].day, '02d') + " -- " \
                 + person[reader.PERSON_NAME] + " -> " + person[reader.PERSON_YEARS]
        if reader.RELATIONS in person:
            names = []
            for relation in person[reader.RELATIONS].keys():
                this_relation = person[reader.RELATIONS][relation]
                this_person = people[relation][reader.PERSON_NAME]
                names.append(this_relation + " of " + this_person)
            output = output + " ---------" + (",".join(names))
        print(output)


def print_all_expired_sorted_month_date(people, sort_key_func):
    people_dead = []
    for person in people.values():
        genealogy_reader.GenealogyReader.decode_years(person)
        if reader.PERSON_DEAD_DATE in person:
            people_dead.append(person)

    people_dead.sort(key=sort_key_func)
    for person in people_dead:
        output = format(person[reader.PERSON_DEAD_DATE].month, '02d') + "-" \
                 + format(person[reader.PERSON_DEAD_DATE].day, '02d') + " -- " \
                 + person[reader.PERSON_NAME] + " -> " + person[reader.PERSON_YEARS]
        if reader.RELATIONS in person:
            names = []
            for relation in person[reader.RELATIONS].keys():
                this_relation = person[reader.RELATIONS][relation]
                this_person = people[relation][reader.PERSON_NAME]
                names.append(this_relation + " of " + this_person)
            output = output + " ---------" + (",".join(names))
        print(output)

def all_people():
    gr = src.reader.genealogy_reader.GenealogyReader()
    people = gr.load_people()
    print_all_expired_sorted_month_date(people, sort_key_by_month_and_day)

if __name__ == '__main__':
    all_people()
