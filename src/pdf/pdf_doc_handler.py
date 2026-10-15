# https://www.blog.pythonlibrary.org/2018/02/06/reportlab-101-the-textobject/

# https://www.quora.com/How-do-I-create-a-Python-program-that-takes-a-users-input-and-places-it-in-a-PDF-file
# https://www.reportlab.com/docs/reportlab-userguide.pdf

# reportlab HTML like stuff
# http://www.blog.pythonlibrary.org/2013/07/19/reportlab-all-about-fonts/

# pip install reportlab

import math
import os
from dataclasses import dataclass
# to manage user input
from textwrap import TextWrapper
from typing import Optional

# to work with pdf
import reportlab.lib.pagesizes as r_page_sizes
import reportlab.pdfbase.pdfmetrics as r_metrics
import reportlab.pdfgen.canvas as r_canvas
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfgen.textobject import PDFTextObject


@dataclass(frozen=True)
class FontType:
    font: str
    size:int
    
DEFAULT_FONT = FontType(font= "Times-Roman", size= 10)


def angle_to_rad(angle : float) -> float:
    pi180 = math.pi / 180
    return angle * pi180

def rad_to_angle(angle:float)-> float:
    pi180 = math.pi / 180
    return angle / pi180


# angle in degrees
def angle_to_transform(angle : float, counterclockwise:bool=False, perpendicular : int=0) -> tuple[float,float,float,float]:
    co = math.cos(angle_to_rad(angle + perpendicular * 90))
    si = math.sin(angle_to_rad(angle + perpendicular * 90))
    if counterclockwise:
        return co, -si, si, co
    else:
        return co, si, -si, co


# angle in degrees
def angle_and_distance_to_xy(angle:float, radius:float) -> tuple[float,float]:
    x = math.cos(angle_to_rad(angle)) * radius
    y = math.sin(angle_to_rad(angle)) * radius
    return x, y


# x offset, y offset are on the normal x,y plane, we need to rotate then angle degrees
def translate_angle_and_distance_to_xy(angle :float, x: float, y:float, counterclockwise:bool=False, perpendicular: int=0) -> tuple[float,float]:
    a, b, c, d = angle_to_transform(angle, counterclockwise=not counterclockwise, perpendicular=perpendicular)
    x1 = a * x + b * y
    y1 = c * x + d * y
    return x1, y1


# look in directory for standard fonts: import reportlab.fonts
# The default page size is A4 (595.27 by 841.89) for reportlab
class PdfHandler:
    font:FontType
    canvas: Canvas
    filename: str

    #  response = HttpResponse(content_type='application/pdf')
    def __init__(self, filename, pagesize=r_page_sizes.LETTER, response=None, font_name=None, font_size=None):
        if not filename.endswith(".pdf"):
            filename += ".pdf"

        if response:
            response['Content-Disposition'] = 'attachment; filename="' + filename + '"'
            self.canvas = r_canvas.Canvas(response, pagesize=pagesize)
        else:
            self.canvas = r_canvas.Canvas(filename, pagesize=pagesize)
            full_name = os.path.join(os.path.abspath(os.getcwd()), filename)
            self.filename = full_name
        self.font = DEFAULT_FONT
        if font_name:
            self.font = FontType(font_name, self.font.size) 
        if font_size:
            self.font = FontType(self.font.font, font_size)
        self.__set_font(self.canvas, self.font)

    @classmethod
    def __set_font(cls, pdf_object : PDFTextObject|Canvas, font : FontType) -> None:
        if font:
            pdf_object.setFont(font.font, font.size)

    def text_height(self, font:Optional[FontType]=None) -> float:
        if not font:
            font = self.font
        h = r_metrics.TypeFace(font.font)
        return ((h.ascent - h.descent) * font.size) / 1000

    def end_page_and_save(self) -> None:
        self.end_page()
        self.canvas.save()

    def end_page(self)-> None:
        self.canvas.showPage()

    def display_file(self) -> None:
        os.startfile(self.filename)

    def size_of_text(self, text, font: Optional[FontType]=None) -> float:
        if not font:
            font = self.font
        return r_metrics.stringWidth(text, font.font, font.size)

    def draw_line(self, x1:float, y1:float, x2:float, y2:float) -> None:
        self.canvas.line(x1, y1, x2, y2)

    def draw_circle_arc(self, x_c:float, y_c:float, radius:float,
                        start_angle:float, end_angle:float) -> None:
        # angles are in degrees not rads
        self.canvas.arc(x_c - radius, y_c - radius, x_c + radius, y_c + radius, start_angle, end_angle)

    # centered = will be centered on x,y
    def multi_line_text(self, text:str, x:float, y:float, font:Optional[FontType]=None,
                        centered:bool=False, top_corner:bool=False) -> None:
        lines = text.split("\n")
        offsets = []
        if not font:
            font = self.font
        if not centered:
            offsets = [0] * len(lines)
        else:
            for line in lines:
                offsets.append(self.canvas.stringWidth(line, font.font, font.size))
            max_width = max(offsets)
            offsets = [(max_width - i) / 2 for i in offsets]
            if not top_corner:
                x -= max_width / 2
                y -= self.text_height(font) / 2 * len(lines)

        tx = self.canvas.beginText(x, y)
        self.__set_font(tx, font)
        for offset, line in zip(offsets, lines):
            tx.setXPos(offset)
            tx.textLine(line)
            tx.setXPos(-offset)
        self.canvas.drawText(tx)

    def text_block_paging(self, text_block:str, pos_x_px:float=100, pos_y_px:float=0,
                          max_lines:int=45, auto_new_page:bool=False, font : Optional[FontType] = None):
        if not font:
            font = self.font
        # Split the text into a list of lines, since
        # we can only write single lines to the PDF
        user_in_lines = text_block.split('\n')

        # Now we need to wrap the user input, so it doesn't go past
        # the right page border
        wrapper = TextWrapper()
        user_in_wrapped_lines = list()

        for line in user_in_lines:
            user_in_wrapped_lines += wrapper.wrap(line)

        # Write the text to the pdf canvas
        count = 0
        text_object: PDFTextObject = self.canvas.beginText(pos_x_px, pos_y_px)
        self.__set_font(text_object, font)

        for line in user_in_wrapped_lines:
            text_object.textLine(line)

            count += 1
            if count == max_lines:
                if auto_new_page:
                    self.canvas.showPage()
                    text_object = self.canvas.beginText(pos_x_px, pos_y_px)
                    count = 0
                else:
                    return
            self.canvas.drawText(text_object)

    def text_rotated(self, x:float, y:float, line:str, font:Optional[FontType]=None,
                     angle:float=0, centered:bool=False) -> None:
        if not font:
            font = self.font
        if centered:
            max_width = self.canvas.stringWidth(line, font.font, font.size)
            offset = max_width / 2
        else:
            offset = 0
        tx = self.canvas.beginText(x, y)

        self.__set_font(tx, font)

        a, b, c, d = angle_to_transform(angle, perpendicular=0)
        tx.setTextTransform(a, b, c, d, x - offset, y)
        tx.textLine(line)

        self.canvas.drawText(tx)

    def text_rotated_bounding_box(self, c_x:float, c_y:float, radius:float, text:str,
                                  angle:float, max_angle:float, max_length:float,
                                  font:Optional[FontType]=None) -> None:
        if not font:
            font = self.font

        lines = []

        this_line = ""
        words = text.split(' ')
        for word in words:
            if word[0] == '\n':
                lines.append(this_line)
                this_line = word[1:]
            else:
                if max_length \
                        and max_length < r_metrics.stringWidth(this_line + ' ' + word, font.font, font.size):
                    this_line += ' ' + word
                else:
                    lines.append(this_line)
                    this_line = word
        lines.append(this_line)

        # angles go backwards
        mid_angle = angle  - max_angle / 2
        a, b, c, d = angle_to_transform(mid_angle, counterclockwise=False)
        x, y = angle_and_distance_to_xy(mid_angle, radius)

        line_cnt = 0- len(lines) / 2
        for line in lines:
            # there is a single x,y, transformation matrix per object, so we set it in the one transform
            tx = self.canvas.beginText()

            self.__set_font(tx, font)
            offset_y = line_cnt * self.text_height()
            line_cnt += 1
            offset_x = 0

            m, n = translate_angle_and_distance_to_xy(mid_angle, offset_x, - offset_y, counterclockwise=False)

            tx.setTextTransform(a, b, c, d, c_x + x + m, c_y + y + n)

            # AFTER setting the transform we can set the text (doesn't work the other way)
            tx.textLine(line)
            self.canvas.drawText(tx)

    # circular_string
    def circular_string_bounding_box(self,
                                     circle_center_x:float, circle_center_y:float,
                                     circle_radius_to_text:float,
                                     text:str,
                                     angle_start:float=0,
                                     font:Optional[FontType]=None,
                                     text_inside_circle:float=0,
                                     centered:bool=False,
                                     max_angle:float=360) -> None:

        if not font:
            font = self.font
        # width = r_metrics.stringWidth(text, font.font, font.size)
        text_direction = text_inside_circle and -1 or 1
        #  is a "font" class which has a fontname and a size e.g. "Helvetica",8

        half_text_direction = text_direction * 0.5

        # insert returns to ensure line not too long
        circle_radius_to_text_run = circle_radius_to_text
        current_angle = 0
        for x in range(len(text)):
            letter = text[x]
            if letter == '\n':
                circle_radius_to_text_run -= self.text_height(font)
                current_angle = 0
            else:
                width = r_metrics.stringWidth(letter, font.font, font.size)
                beta = float(width) / circle_radius_to_text_run
                current_angle += rad_to_angle(text_direction * beta)  # increment
                if current_angle >= max_angle:
                    circle_radius_to_text_run -= self.text_height(font)
                    current_angle = 0
                    y = x
                    while y > 0 and text[y] != " " and text[y] != '\n':
                        y -= 1
                    if y > 0:
                        text = text[:y] + '\n' + text[y + 1:]

        offsets = []
        if centered:
            circle_radius_to_text_run = circle_radius_to_text
            current_angle = 0
            for letter in text:
                if letter == '\n':
                    offsets.append((max_angle - current_angle) / 2)
                    circle_radius_to_text_run -= self.text_height(font)
                    current_angle = 0
                else:
                    width = r_metrics.stringWidth(letter, font.font, font.size)
                    beta = float(width) / circle_radius_to_text_run
                    current_angle += rad_to_angle(text_direction * beta)  # increment
                    if current_angle >= max_angle:
                        offsets.append((max_angle - current_angle) / 2)
                        circle_radius_to_text_run -= self.text_height(font)
                        current_angle = 0
            offsets.append((max_angle - current_angle) / 2)

        circle_radius_to_text_run = circle_radius_to_text
        current_angle = 0
        line = 0
        for letter in text:
            if letter == '\n':
                circle_radius_to_text_run -= self.text_height(font)
                current_angle = 0
                line += 1
            else:
                width = r_metrics.stringWidth(letter, font.font, font.size)
                beta = float(width) / circle_radius_to_text_run
                current_phi = angle_start - current_angle
                if centered:
                    current_phi -= offsets[line]
                x, y = angle_and_distance_to_xy(current_phi, circle_radius_to_text_run)
                self.text_rotated(
                    circle_center_x + x,
                    circle_center_y + y,
                    letter,
                    font=font,
                    angle=current_phi - half_text_direction * rad_to_angle(beta)  - (text_direction *90))
                current_angle += rad_to_angle(text_direction * beta)  # increment
                if current_angle >= max_angle:
                    circle_radius_to_text_run -= self.text_height(font)
                    current_angle = 0
                    line += 1
