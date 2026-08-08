from tkinter import *

FIELD = "field"
TEXT_FROM_STAT_OF_FIELD = "1.0"
TEXT_TO_END_OF_FIELD = "end-1c"


# can't mix grid and pack in the same frame
# pack causes text to be packed (depending on the option)
# place places the text at specific positions 0%- 100%
# grid creates a grid, but empty items are not considered

class UserInput:

    def __init__(self, title="Python Window", size_x=900, size_y=600):
        self.window = Tk()
        self.window.title(title)
        self.window.geometry("{0}x{1}".format(size_x, size_y))
        self.input_frame = Frame(self.window, width=size_x, height=size_y - 50)
        self.input_frame.pack(side=TOP)
        self.button_frame = Frame(self.window, width=size_x, height=50)
        self.button_frame.pack(side=BOTTOM)

        self.input_fields = []
        self.grid_row = 0
        self.grid_column = 0
        self.size_x = size_x
        self.size_y = size_y

    def __end_form__(self):
        self.input_fields = None
        self.window.destroy()
        self.window = None

    def __fail_on_no_window__(self):
        if not self.window:
            raise ReferenceError("Window not initialized")

    def add_input_field(self, label_value, g_row=None, g_col=None, input_width=50):
        self.__fail_on_no_window__()
        if not g_row:
            g_row = self.grid_row + 1
        if not g_col:
            g_col = self.grid_column

        label = Label(self.input_frame, text=label_value)
        label.grid(row=g_row, column=g_col, padx=5, pady=5)

        txt_var = StringVar(None)
        usr_in = Entry(self.input_frame, textvariable=txt_var, width=input_width)
        usr_in.grid(row=g_row, column=g_col + 1, padx=5, pady=5)

        self.input_fields.append(txt_var)
        self.grid_row = g_row
        self.grid_column = g_col

    def execute_form(self, submit_text="Submit"):
        self.__fail_on_no_window__()
        # Pass an array * By reference passing trick
        user_input = []

        def submit():
            # This function will be called once the user clicks
            # the "submit" button. It saves the user's text to a
            # variable and then closes the window
            for field in self.input_fields:
                user_input.append(field.get())

            self.__end_form__()

        submit_button = Button(self.button_frame, text=submit_text, command=submit)
        submit_button.pack(side=BOTTOM)
        self.window.mainloop()
        # The program will automatically pause here until the
        # user clicks on the submit button

        return user_input


if __name__ == '__main__':
    ux = UserInput()
    ux.add_input_field("Hello1")
    ux.add_input_field("Hello2 ")
    results = ux.execute_form("Press when finished")
    print(results)
