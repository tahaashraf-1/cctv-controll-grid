from tkinter import*
from PIL import Image,ImageTk
from record import record

root = Tk()
root.title("live CCTV camera")
root.geometry("1080x600")


mainframe = Frame(root, bd=2)
label_title= Label(mainframe,text='live cctv camera',font=('Helvitica', 25, 'bold'))
label_title.grid(pady=(10,10),column=2)

btn_image=Image.open('recording.ico')
btn_image=btn_image.resize((50,50))
btn_image_tk=ImageTk.PhotoImage(btn_image)

btn= Button(mainframe,font=('Helvitica', 25, 'bold'),text='VideoRecord', height=90,
            width=270,fg='orange', image=btn_image_tk,compound='left', command=record)
btn.grid(row=2,pady=(20,10),column=1)


logout_image=Image.open('logout.ico')
logout_image=logout_image.resize((50,50))
logout_image_tk=ImageTk.PhotoImage(logout_image)

exit_btn= Button(mainframe,font=('Helvitica', 25, 'bold'),text='Exit', height=90,
            width=270,fg='orange', image=logout_image_tk,compound='left',command=root.quit)
exit_btn.grid(row=3,pady=(20,10),column=1)









mainframe.pack()




root.mainloop()


