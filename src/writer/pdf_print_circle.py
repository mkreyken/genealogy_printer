import math
import re
import reportlab.lib.pagesizes as r_page_sizes

import src.reader.genealogy_reader
from src import reader
from src.pdf.pdf_doc_handler import PdfHandler

DEFAULT_PAGE_SIZE = r_page_sizes.LETTER
DEFAULT_FONT_SIZE = 7
CENTER_X = DEFAULT_PAGE_SIZE[0] / 2
CENTER_Y = DEFAULT_PAGE_SIZE[1] / 2

# replaces all multi spaces with single spaces and removed all () and strip all end " "
def simple_name(name):
    return re.sub(r"\s+", " ", re.sub(r"\([^)]*\)", "", name, 0, re.MULTILINE)).strip()


def angle_to_rad(angle):
    pi180 = math.pi / 180
    return angle * pi180

# standard angles, our angle system starts at 180o and goes around
def find_x_y(angle, distance):
    x = distance * math.cos(angle_to_rad(angle)) + CENTER_X
    y = distance * math.sin(angle_to_rad(angle)) + CENTER_Y
    return [x, y]


# after 3 levels the text rows get so big we should rotate the text and allow for 17 characters

LEVEL_SIZE = [0, 25, 50, 75, 140, 220, 310, 460, 500, 500, 500, 500, 500, 500, 500]
LEVEL_TEXT_DIRECTION = [0,0,0,0, 1, 1, 1, 1, 1]


class CircleOutput:
    def __init__(self, people, pdf):
        self.people = people
        self.pdf = pdf

    def draw_center(self, person):
        name = simple_name(person[reader.PERSON_NAME])
        self.pdf.multi_line_text(
            name,
            x=CENTER_X,
            y=CENTER_Y, centered=True)

    def draw_person(self, person, level, s_angle, e_angle):
        if level == 0:
            self.draw_center(person)
            return
        name = simple_name(person[reader.PERSON_NAME])
        # angles go counterclockwise, but text is clockwise, so convert 0-360 "clockwise" to draw linear counter
        s_adjusted = 180 + 360 - s_angle
        e_adjusted = 180 + 360 - e_angle
        if LEVEL_TEXT_DIRECTION[level] == 1:
            self.pdf.text_rotated_bounding_box(
                CENTER_X, CENTER_Y,
                LEVEL_SIZE[level-1]+  (DEFAULT_FONT_SIZE * 1.1) ,
                name,
                angle=s_adjusted,
                max_length = LEVEL_SIZE[level] - LEVEL_SIZE[level-1],
                max_angle =s_adjusted - e_adjusted)

        else:
            self.pdf.circular_string_bounding_box(
                CENTER_X, CENTER_Y,
                LEVEL_SIZE[level] - (DEFAULT_FONT_SIZE * 1.1),
                name,
                angle_start=s_adjusted, max_angle=s_adjusted - e_adjusted,
                centered=True)

        self.pdf.draw_circle_arc(
                CENTER_X, CENTER_Y,
                LEVEL_SIZE[level] ,
                s_adjusted, s_adjusted - e_adjusted)

    # Parents do a range of the circle in angles (first parents 0-360,
    # second parents align with each of the first 4 parents)
    def walk_parents(self, person, level, start_angle, end_angle):
        try:
            if level > 7:
                return

            self.draw_person(person, level, start_angle, end_angle)
            if not person.get(reader.PERSON_PARENTS):
                return
            angles = (end_angle - start_angle) / len(person[reader.PERSON_PARENTS])
            s_angle = start_angle
            for parent_id in person[reader.PERSON_PARENTS]:
                parent = self.people[parent_id]
                self.walk_parents(parent, level + 1, s_angle, s_angle + angles)
                s_angle += angles
        except Exception as ex:
            print(person)
            raise ex


def run():
    gr = src.reader.genealogy_reader.GenealogyReader()
    people = gr.load_people()
    pdf = PdfHandler("user_reader.pdf", pagesize=DEFAULT_PAGE_SIZE, font_size=DEFAULT_FONT_SIZE)
    co = CircleOutput(people, pdf)
    do_person = people["person_id"]
    co.walk_parents(do_person, 0, 0, 360)
    # Save the pdf file
    pdf.end_page_and_save()
    pdf.display_file()


if __name__ == '__main__':
    run()
