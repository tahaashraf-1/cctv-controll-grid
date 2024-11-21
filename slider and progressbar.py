import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext

parent = tk.Tk()

parent.title('slider and progressbar')
scale_float = tk.DoubleVar(value = 15)
scale = ttk.Scale(parent,from_ = 0, to = 25,command = lambda value:progress.stop(),length = 300,
                  orient = 'horizontal',variable= scale_float)
scale.pack()

# progress = ttk.Progressbar(parent, variable = scale_float,
# maximum = 25, orient = 'horizontal',length = 300,
#                            mode = 'indeterminate')
# progress.pack()
# progress.start()
# scrolled_text = scrolledtext.ScrolledText(parent, width = 100, height = 20)
# scrolled_text.pack()


# exercise_int = tk.IntVar()
# exercise_progress =ttk.Progressbar(parent, orient = 'vertical', variable = exercise_int)
# exercise_progress.pack()
# exercise_progress.start()
#
# label = ttk.Label(parent,textvariable = exercise_int)
# label.pack()
# exercise_scale = ttk.Scale(parent, variable= exercise_int, from_ = 0, to = 100)
# exercise_scale.pack()










parent.mainloop()