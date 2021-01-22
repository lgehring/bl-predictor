import datetime
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import *

from teamproject.gui_slider_widget import Slider

root = Tk()
root.title('Learn To Code at Codemy.com')
# root.iconbitmap('c:/gui/codemy.ico')
root.geometry("500x400")

# Create A Main Frame
main_frame = Frame(root)
main_frame.pack(fill=BOTH, expand=1)

# Create A Canvas
my_canvas = Canvas(main_frame)
my_canvas.pack(side=LEFT, fill=BOTH, expand=1)

# Add A Scrollbar To The Canvas
my_scrollbar = ttk.Scrollbar(main_frame, orient=VERTICAL,
                             command=my_canvas.yview)
my_scrollbar.pack(side=RIGHT, fill=Y)

# Configure The Canvas
my_canvas.configure(yscrollcommand=my_scrollbar.set)
my_canvas.bind('<Configure>', lambda e: my_canvas.configure(
    scrollregion=my_canvas.bbox("all")))

# Create ANOTHER Frame INSIDE the Canvas
second_frame = Frame(my_canvas)

# Add that New frame To a Window In The Canvas
my_canvas.create_window((0, 0), window=second_frame, anchor="nw")


# TODO: define elements
def _timeframe_slider():
    """
    Builds a slider ro adjust the to crawl period.
    """
    date_label = tk.Label(second_frame, text="Choose a period of time:")
    date_label.pack()

    first_recorded_bl_year = 2003  # 1964, Openliga has only new matches
    slider = Slider(second_frame, width=400,
                    height=60,
                    min_val=first_recorded_bl_year,
                    max_val=datetime.datetime.now().year,
                    init_lis=[first_recorded_bl_year + 0.4,  # padding
                              datetime.datetime.now().year],
                    show_value=True)
    return slider


# TODO: add elements
_timeframe_slider().pack()

root.mainloop()
