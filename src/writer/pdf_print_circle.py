import math
import re
from typing import List

import reportlab.lib.pagesizes as r_page_sizes

import src.reader.genealogy_reader
from models.people import Person
from src.pdf.pdf_doc_handler import PdfHandler, angle_and_distance_to_xy

DEFAULT_PAGE_SIZE = r_page_sizes.LETTER
DEFAULT_FONT_SIZE = 7
CENTER_X = DEFAULT_PAGE_SIZE[0] / 2
CENTER_Y = DEFAULT_PAGE_SIZE[1] / 2

# replaces all multi spaces with single spaces and removed all () and strip all end " "
def simple_name(name: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"\([^)]*\)", "", name, 0, re.MULTILINE)).strip()


def angle_to_rad(angle: float) -> float:
    pi180 = math.pi / 180
    return angle * pi180


# standard angles, our angle system starts at 180o and goes around
def find_x_y(angle: float, distance: float) -> tuple[float, float]:
    x = distance * math.cos(angle_to_rad(angle)) + CENTER_X
    y = distance * math.sin(angle_to_rad(angle)) + CENTER_Y
    return x, y


# after 3 levels the text rows get so big we should rotate the text and allow for 17 characters

LEVEL_SIZE: List[int] = [0, 35, 65, 95, 140, 185, 230, 275,320]
LEVEL_TEXT_DIRECTION : List[int]= [0, 0, 0, 0, 1, 1, 1, 1, 1]


class CircleOutput:
    people: dict[str, Person]
    pdf: PdfHandler

    def __init__(self, people, pdf) -> None:
        self.people = people
        self.pdf = pdf

    def draw_center(self, person: Person) -> None:
        name = "\n".join(simple_name(person.name).split())
        self.pdf.multi_line_text(
            name,
            x=CENTER_X,
            y=CENTER_Y, centered=True, top_corner=False)

    def draw_person(self, person: Person, level: int, s_angle: float, e_angle: float) -> None:
        if level == 0:
            self.draw_center(person)
            return
        name = simple_name(person.name)
        # angles go counterclockwise, but text is clockwise, so convert 0-360 "clockwise" to draw linear counter
        s_adjusted = 180 + 360 - s_angle
        e_adjusted = 180 + 360 - e_angle
        if LEVEL_TEXT_DIRECTION[level] == 1:
            self.pdf.text_rotated_bounding_box(
                CENTER_X, CENTER_Y,
                LEVEL_SIZE[level - 1] + (DEFAULT_FONT_SIZE * .5),
                name,
                angle=s_adjusted,
                max_length=LEVEL_SIZE[level] - LEVEL_SIZE[level - 1] - (DEFAULT_FONT_SIZE * 1.0),
                max_angle=s_adjusted - e_adjusted)

        else:
            self.pdf.circular_string_bounding_box(
                CENTER_X, CENTER_Y,
                LEVEL_SIZE[level] - (DEFAULT_FONT_SIZE * 1.1),
                name,
                angle_start=s_adjusted, max_angle=s_adjusted - e_adjusted,
                centered=True)


    # Parents do a range of the circle in angles (first parents 0-360,
    # second parents align with each of the first 4 parents)
    def walk_parents(self, person: Person, level: int, start_angle: float, end_angle: float) -> None:
        try:
            if level > len(LEVEL_SIZE)-1:
                return

            self.draw_person(person, level, start_angle, end_angle)
            parent_ids = person.parent_ids()
            if not parent_ids:
                return
            angles = (end_angle - start_angle) / 2 # len(parent_ids)
            s_angle = start_angle
            for parent_id in parent_ids:
                parent = self.people[parent_id]
                self.walk_parents(parent, level + 1, s_angle, s_angle + angles)
                s_angle += angles
        except Exception as ex:
            print(person)
            raise ex

    def draw_lines(self) -> None:
        max_level = len(LEVEL_SIZE)-1
        for level in range(1, max_level+1):
            self.pdf.draw_circle_arc(
                CENTER_X, CENTER_Y,
                LEVEL_SIZE[level],
                0, 360)
            if level == 1:
                angles = [0,180]
            elif level == 2:
                angles = [90,270]
            elif level >= max_level-1:
                continue
            else:
                step = 180 / (2 ** (level - 2))
                start = step / 2
                angles = [start + i * step for i in range(int(360 / step))]
            for i in angles:
                x1, y1 = angle_and_distance_to_xy(i, LEVEL_SIZE[level])
                x2, y2 = angle_and_distance_to_xy(i, LEVEL_SIZE[max_level])
                self.pdf.draw_line(
                    CENTER_X + x1,
                    CENTER_Y + y1,
                    CENTER_X + x2,
                    CENTER_Y + y2
                )



def run() -> None:
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
