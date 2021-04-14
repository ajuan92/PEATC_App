import os
import sys
from time import time
from tkinter import *
from tkinter.ttk import Combobox
from tkinter import ttk

from random import randint

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

Test_AS_Raw_Data_6_month = [5, 65533, 65532, 0, 3, 2, 65535, 65534, 65535, 0, 0, 2, 10, 25, 41, 46, 36, 13, 65524, 65507, 65500, 65502, 65508, 65517, 65529, 7, 21, 28, 27, 18, 8, 65533,
                            65521, 65510, 65502, 65506, 65525, 18, 44, 56, 51, 32, 10, 65526, 65504, 65480, 65455, 65438, 65435, 65447, 65466, 65485, 65500, 65516, 0, 22, 38, 42, 36, 26, 23, 26, 31, 0, 18, 5]

Test_AS_Raw_Data_12_month = [2, 0, 1, 0, 65535, 1, 1, 65535, 65535, 1, 0, 65535, 6, 26, 43, 43, 27, 8, 65527, 65509, 65490, 65483, 65492, 65508, 65522, 65535, 14, 30, 35, 28, 14,
                             65533, 65518, 65511, 65515, 65532, 18, 36, 43, 36, 18, 65534, 65517, 65502, 65483, 65463, 65452, 65456, 65474, 65494, 65511, 65527, 9, 30, 44, 41, 23, 8, 13, 33, 46, 37, 15, 2]

Test_AS_Raw_Data_20_month = [4, 65535, 65535, 0, 1, 0, 65535, 0, 2, 1, 65534, 1, 17, 38, 50, 44, 25, 0, 65514, 65501, 65501, 65513, 65531, 13, 29, 39, 35, 20, 2, 65522, 65506, 65492,
                             65489, 65502, 65523, 6, 23, 39, 45, 33, 10, 65526, 65512, 65497, 65476, 65455, 65442, 65440, 65448, 65464, 65482, 65496, 65507, 65521, 3, 19, 28, 34, 41, 42, 33, 17, 4, 0, 0, 0]

PEATC_CONFIG_SAMPLE_WAIT_TIME = 10
PEATC_CONFIG_DIAG_WAIT_TIME = 10
'''!
Comandos
'''
PEATC_CONFIG_CMD_START_TEST = 1
PEATC_CONFIG_CMD_STOP_TEST = 2

Cmd_Template = {
    "Cmd": 0,
    "Gs_SignaldB": 0,
    "Gs_Latency": 0,
    "Gs_Polarity": 0,
    "Gs_Freq": 0,
}

'''!
Estado Stand by
'''
STATE_STAND_BY = 0
STATE_RESET = 1
STATE_INIT_TEST = 2
STATE_WAIT_RAW_DATA = 3
STATE_ANALYZE_DATA = 4
STATE_INIT_DIAGNOSTIC = 5
STATE_WAIT_DIAGNOSTIC = 6
STATE_SEND_RESULT = 7


Window = Tk()
Window.title("PEATC_APP")
Window.geometry("1000x600")

WindowFrame = Frame(Window)
WindowFrame.pack(fill="both", expand=1)
WindowFrame.config(bg="white")

BtnFrame = Frame(WindowFrame)
BtnFrame.pack(fill="both", side="right", expand=1)
BtnFrame.config(bg="white")
BtnFrame.config(width="400", height="400")


GrafFrame = Frame(WindowFrame)
GrafFrame.pack(fill="both", side="left", expand=1)
GrafFrame.config(bg="white")
GrafFrame.config(width="600", height="400")

Graf_Notebook = ttk.Notebook(GrafFrame, width="600", height="400")
Graf_Notebook.place(x=10, y=1)
GrafTab = ttk.Frame(Graf_Notebook)
WaveTab = ttk.Frame(Graf_Notebook)
Graf_Notebook.add(GrafTab, text='First')
Graf_Notebook.add(WaveTab, text='Second')
Graf_Notebook.pack(fill='both', expand=True)

scroll_bar = Scrollbar(GrafTab)
scroll_bar.pack(side=RIGHT, fill=Y)


fig = Figure(figsize=(5, 4), dpi=100)
fig.set_figheight(100)
ax = fig.add_subplot(5, 1, 1)
ax.legend(['Stock_Index_Price'])
ax.set_xlabel('Interest Rate')
ax.set_title('Interest Rate Vs. Stock Index Price')

canvas = FigureCanvasTkAgg(fig, master=GrafTab)
canvas.get_tk_widget().grid_propagate(0)
canvas.get_tk_widget().config(bg='#FFFFFF', scrollregion=(0, 0, 500, 500))
canvas.get_tk_widget().config(width=300, height=1000)
canvas.get_tk_widget().config(xscrollcommand=scroll_bar.set)

canvas.get_tk_widget().pack(side="top", fill="both")

scroll_bar.config(command=canvas.get_tk_widget().yview)


def clicked():
    fig.clear()
    fig.add_subplot(5, 1, 1).plot([randint(0, 10), randint(
        0, 10), randint(0, 10), randint(0, 10)], [4, 3, 2, 1])
    fig.add_subplot(5, 1, 2).plot([randint(0, 10), randint(
        0, 10), randint(0, 10), randint(0, 10)], [4, 3, 2, 1])
    fig.add_subplot(5, 1, 3).plot([randint(0, 10), randint(
        0, 10), randint(0, 10), randint(0, 10)], [4, 3, 2, 1])
    fig.add_subplot(5, 1, 4).plot([randint(0, 10), randint(
        0, 10), randint(0, 10), randint(0, 10)], [4, 3, 2, 1])
    fig.add_subplot(5, 1, 5).plot([randint(0, 10), randint(
        0, 10), randint(0, 10), randint(0, 10)], [4, 3, 2, 1])
    canvas.draw()


btn = Button(BtnFrame, text="Click Me", command=clicked)
btn.place(bordermode=OUTSIDE, height=80, width=200, x=100, y=200)


Window.mainloop()
