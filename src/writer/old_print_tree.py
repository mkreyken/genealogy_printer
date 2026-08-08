# https://www.blog.pythonlibrary.org/2018/02/06/reportlab-101-the-textobject/

# https://www.quora.com/How-do-I-create-a-Python-program-that-takes-a-users-input-and-places-it-in-a-PDF-file
# https://www.reportlab.com/docs/reportlab-userguide.pdf

# reportlab HTML like stuff
# http://www.blog.pythonlibrary.org/2013/07/19/reportlab-all-about-fonts/
# pip install reportlab
import math
import os
# to manage user input
from textwrap import TextWrapper
from tkinter import Tk, Button, Text
from typing import List

# to work with pdf
import reportlab.graphics.shapes as r_shapes
import reportlab.lib.pagesizes as r_page_sizes
import reportlab.pdfbase.pdfmetrics as r_metrics
import reportlab.pdfgen.canvas as r_canvas


# look in directory for standard fonts: import reportlab.fonts

def get_text():
    # Create a simple interface that allows the user
    # to enter text over multiple lines

    # Initialize the GUI
    top = Tk()
    input_field = Text(top)
    input_field.pack()
    # Pass an array * By reference passing trick
    user_in = [""]

    def submit():
        # This function will be called once the user clicks
        # the "submit" button. It saves the user's text to a
        # variable and then closes the window

        user_in[0] = input_field.get(1.0, "end-1c")
        top.destroy()

    submit_button = Button(top, text="submit", command=submit)
    submit_button.pack()
    top.mainloop()
    # The program will automatically pause here until the
    # user clicks on the submit button

    return user_in[0]


def write_into_pdf(canvas, user_in):
    # Now write the text to our PDF file
    # We will use a padding of 100pt at each side of the page

    # Split the text into a list of lines, since
    # we can only write single lines to the PDF
    user_in_lines = user_in.split('\n')

    # Now we need to wrap the user input, so it doesn't go past
    # the right page border
    wrapper = TextWrapper()
    user_in_wrapped_lines = list()

    for line in user_in_lines:
        user_in_wrapped_lines += wrapper.wrap(line)

    # Write the text to the pdf canvas
    count = 0
    text_object = canvas.beginText(100, 741.89)

    for line in user_in_wrapped_lines:
        text_object.textLine(line)
        count += 1
        if count == 45:
            # We need to create a new text_object for the new page
            canvas.drawText(text_object)
            canvas.showPage()
            text_object = canvas.beginText(100, 741.89)
            count = 0

    canvas.drawText(text_object)

def create_multi_line_text_object(canvas, x, y, text, font_name, font_size, centered=False):
    lines = text.split("\n")
    offsets : List[int] = []
    if centered:
        for line in lines:
            offsets.append(canvas.stringWidth(line, font_name, font_size))
        max_width = max(offsets)
        offsets = [int((max_width - i) / 2) for i in offsets]
    else:
        offsets = [0] * len(lines)
    tx = canvas.beginText(x, y)
    tx.setFont(font_name, font_size)
    for offset, line in zip(offsets, lines):
        tx.setXPos(offset)
        tx.textLine(line)
        tx.setXPos(-offset)
        tx.direction()
    canvas.drawText(tx)


def create_text_rotated(canvas, x, y, line, font_name, font_size, angle=0, centered=False):
    if centered:
        max_width = canvas.stringWidth(line, font_name, font_size)
        offset = max_width / 2
    else:
        offset = 0
    tx = canvas.beginText(x, y)
    tx.setFont(font_name, font_size)
    co = math.cos(angle * math.pi / 180.0)
    si = math.sin(angle * math.pi / 180.0)
    tx.setTextTransform(co, -si, si, co, x - offset, y)
    tx.textLine(line)
    canvas.drawText(tx)


def angle_to_rad(angle) :
    pi180 = math.pi / 180
    return angle * pi180

def make_circular_string(canvas,
                         circle_center_x, circle_center_y,
                         circle_radius_to_text, phi_start,
                         text,
                         font_name, font_size,
                         text_inside_circle=0, text_anchor='start', max_angle= 2 * math.pi):

    width = r_metrics.stringWidth(text, font_name, font_size)
    sig = text_inside_circle and -1 or 1
    #  is a "font" class which has a fontname and a size e.g. "Helvetica",8
    h = r_metrics.TypeFace(font_name)
    text_height = ((h.ascent - h.descent) * font_size) / 1000
    half_sig = sig * 0.5
    sig90 = sig * 90

    if text_anchor != 'start':
        if text_anchor == 'middle':
            phi_start += sig * (0.5 * width) / circle_radius_to_text
        elif text_anchor == 'end':
            phi_start += sig * float(width) / circle_radius_to_text
        elif text_anchor == 'numeric':
            phi_start += sig * float(
                r_shapes.numericXShift(text_anchor, text, width, font_name, font_size, None)) / circle_radius_to_text

    phi = 0
    for letter in text:
        if letter == '\n':
            circle_radius_to_text -= text_height
            phi = 0
        else :
            width = r_metrics.stringWidth(letter, font_name, font_size)
            beta = float(width) / circle_radius_to_text
            current_phi = phi_start - phi
            create_text_rotated(canvas,
                                circle_center_x + math.cos(current_phi) * circle_radius_to_text,
                                circle_center_y + math.sin(current_phi) * circle_radius_to_text,
                                letter, font_name, font_size,
                                int (- ((current_phi - half_sig * beta) * 180 / math.pi - sig90)))  # rotate as needed
            phi += sig * beta  # increment
            if phi >= max_angle:
                phi = 0
                circle_radius_to_text -= text_height


def run():
    # Create a PDF file called "user_input.pdf"
    # in the current directory
    # The default page size is A4 (595.27 by 841.89)
    canvas = r_canvas.Canvas("user_input.pdf", pagesize=r_page_sizes.letter)

    # user_in = get_text()
    # write_into_pdf(canvas, user_in)
    # best guess
    # circle center x,circle center y,circle radius,
    # d = make_circular_string(0, 0, 15, 0, "Hello", 'Times-Roman', 10, ).asDrawing(200, 200)
    # renderPDF.draw(d, canvas, r_pagesizes.letter[0]/2, r_pagesizes.letter[1]/2)
    make_circular_string(canvas,
                         r_page_sizes.letter[0] / 2,
                         r_page_sizes.letter[1] / 2,
                         30, angle_to_rad(180),
                         "Hello This is a test of related text how much is enough before you need to start another line",
                         'Times-Roman', 6, max_angle= angle_to_rad(180))
    make_circular_string(canvas,
                         r_page_sizes.letter[0] / 2,
                         r_page_sizes.letter[1] / 2,
                         50, angle_to_rad(180),
                         "First Name \n Birthday",
                         'Times-Roman', 6)

    # Save the pdf file
    canvas.showPage()
    canvas.save()
    full_name = os.path.join(os.path.abspath(os.getcwd()), "user_input.pdf")
    os.startfile(full_name)


if __name__ == '__main__':
    run()
