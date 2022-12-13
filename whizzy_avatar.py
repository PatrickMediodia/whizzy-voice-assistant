"""
Ideas:
- generate avatar with video of talking then play video using openCV
"""

import tkinter as tk
from PIL import ImageTk, Image

def initialize_avatar():
    window = tk.Tk()
    window.attributes('-zoomed', True)
    #Text
    greeting = tk.Label(text='Hello, world')
    greeting.pack()

    #Image
    image1 = Image.open("images/avatar.png")
    test = ImageTk.PhotoImage(image1)

    labelImage = tk.Label(image=test)
    labelImage.image = test
    labelImage.place(x=0, y=0)

    window.mainloop()

def speaking_avatar():
    pass

def not_speaking_avatar():
    pass
