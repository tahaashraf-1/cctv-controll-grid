import tkinter as tk
from tkinter import  ttk
parent =tk.Tk()
parent.geometry('400x300')
parent.title("buttons")
def button_func():
    print("a basic button")
    print(radio_var.get())

string_var = tk.StringVar(value='newbutton')
button = ttk.Button(parent,text="button",command= button_func, textvariable= string_var)
button.pack()
check_var = tk.StringVar()
check = ttk.Checkbutton(parent,
                        text='checkbutton',
                        command=lambda: print(check_var.get()),
                        variable=check_var)
check.pack()
check1 = ttk.Checkbutton(parent,text='checkbox1',command=lambda:check_var.set(5))
check1.pack()
# radiobutton
radio_var =tk.StringVar()
radio1 = ttk.Radiobutton(parent,text='radiobutton1',
                         value='button 1',command=lambda: print(radio_var.get()),variable=radio_var)
radio1.pack()
radio2 = ttk.Radiobutton(parent,text='radiobutton2',value=2,variable= radio_var)
radio2.pack()
def radio_func():
    print(check_bool.get())
    check_bool.set(False)
radio_string = tk.StringVar()
check_bool = tk.BooleanVar()
check = ttk.Checkbutton(parent,text='checkbutton',variable=check_bool,command=lambda: print(radio_string.get()))
check.pack()
radio1 = ttk.Radiobutton(parent,text='radio1',value='pti',command=radio_func,variable=radio_string)
radio1.pack()
radio2 = ttk.Radiobutton(parent,text='radio2',value='pmln',
                         command=radio_func,variable=radio_string)
radio2.pack()
# run
parent.mainloop()