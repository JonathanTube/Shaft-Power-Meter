from ttkbootstrap import Window, Meter, Entry

root = Window(themename="cosmo")
root.geometry("800x600")

meter = Meter(
    metersize=180,
    padding=5,
    amountused=25,
    metertype="semi",
    subtext="miles per hour",
    interactive=True,
)
meter.pack()

# update the amount used directly
meter.configure(amountused=50)

# update the amount used with another widget
entry = Entry(textvariable=meter.amountusedvar)
entry.pack(fill='x')

# increment the amount by 10 steps
meter.step(10)

# decrement the amount by 15 steps
meter.step(-15)

# update the subtext
meter.configure(subtext="loading...")

root.mainloop()
