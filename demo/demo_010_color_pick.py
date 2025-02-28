from ttkbootstrap import Window, Button, Entry
from ttkbootstrap.dialogs.colorchooser import ColorChooserDialog


def on_color_select(colors):
    entry.delete(0, 'end')  # Clear the current value in the entry
    entry.insert(0, colors.hex)  # Insert the selected color into the entry


root = Window(themename="cosmo")
root.geometry("800x600")

entry = Entry(root)
entry.pack(padx=10, pady=10)


def select_color():
    ccd = ColorChooserDialog(root)
    ccd.show()
    colors = ccd.result
    on_color_select(colors)


button = Button(root, text="Select Color", command=select_color)
button.pack(padx=10, pady=10)


root.mainloop()
