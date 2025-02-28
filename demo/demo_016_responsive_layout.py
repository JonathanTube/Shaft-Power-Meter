
from ttkbootstrap import Window, Frame, Button

root = Window(themename="cosmo")
root.geometry("800x600")

left_frame = Frame(root, bootstyle="light")
left_frame.pack(side="left", fill="y", padx=10)
button = Button(left_frame, text="Click Me")
button.pack()

right_frame = Frame(root, bootstyle="dark")
right_frame.pack(side="right", expand=True, fill="both")

root.mainloop()
