import tkinter as tk
from tkinterhtml import HtmlFrame

root = tk.Tk()
html_frame = HtmlFrame(root)
html_frame.pack(fill="both", expand=True)
html_frame.set_content("<h1>Hello, World!</h1>")
root.mainloop()