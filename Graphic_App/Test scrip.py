import tkinter as tk
from tkinter import *
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


f = Figure(figsize=(1, 1), dpi=100)

a = []

for i in range(0, 20):

    a.append(f.add_subplot(20, 1, i + 1))

f.set_figheight(60)
f.set_figwidth(14)

for i in range(0, 20):

    a[i].plot([1, 2, 3, 4, 5], [1, 2, 3, 4, 5])
    a[i].set_title('Graph ' + str(i + 1))


class App(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand=True)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

        self.minsize(620, 400)

        self.geometry(
            "{0}x{1}+0+0".format(self.winfo_screenwidth(), self.winfo_screenheight()))

        self.update_idletasks()

        self.frames = {}

        for F in (StartPage, PageTwo):

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame(StartPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        button_p1 = tk.Button(self, text="PageTwo →",
                              command=lambda: controller.show_frame(PageTwo))
        button_p1.pack(side=TOP, fill=X)

        label = tk.Label(self, text="Start Page")
        label.pack(fill=X, expand=True)


class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        button_1 = tk.Button(self, text="← Start Page",
                             command=lambda: controller.show_frame(StartPage))
        button_1.pack(side=LEFT, anchor=N)

        label_p1 = tk.Label(self, text="PageTwo")
        label_p1.pack()

        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.X, expand=True)

        scroll = Scrollbar(canvas.get_tk_widget())
        scroll.config(command=canvas.get_tk_widget().yview)
        scroll.pack(side=RIGHT, fill=Y)
        canvas.get_tk_widget().pack(side=LEFT, expand=YES, fill=BOTH)
        canvas.get_tk_widget().config(yscrollcommand=scroll.set)

        canvas.get_tk_widget().config(scrollregion=(0, 0, 1000, 10000), confine=True)


app = App()

app.mainloop()
