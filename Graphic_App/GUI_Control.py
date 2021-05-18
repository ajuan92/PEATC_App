import os
import sys
from time import time
from tkinter import *
from tkinter.ttk import Combobox
from tkinter import ttk

from time import sleep
import struct

import multiprocessing as mprocess
from multiprocessing import Array

CURR_PATH = os.path.dirname(os.path.realpath(__file__))
LOW_DRIVE_PATH = CURR_PATH + "\\..\\Control_Block"

sys.path.append(
    LOW_DRIVE_PATH)

import PEATC_Control as Ctrl

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


class GUI_Control():
    '''!
    Controlador de la aplicación grafica

    @note Este módulo despliega la interfaz grafica que interactua
    con el usuario, así como capturar los comandos y datos generados
    por el usuario.
    '''

    def __init__(self):
        '''!
        Inicializa la maquina de estados para realizar la prueba de PEATC
        '''
        self.__Ctrl_Cmd_output, self.__Ctrl_Cmd_input = mprocess.Pipe(False)
        self.__Ctrl_Result_output, self.__Ctrl_Result_input = mprocess.Pipe(
            False)

        self.__Ctrl_State = Array('i', range(1))

        self.__Diag_Table_output, self.__Diag_Table_input = mprocess.Pipe(
            False)
        self.__Diag_Result_output, self.__Diag_Result_input = mprocess.Pipe(
            False)

        self.__Diag_State = Array('i', range(1))

        self.__Ctrl_Block = Ctrl.PEATC_Control()

        self.__Ctrl_Task = mprocess.Process(target=self.__Ctrl_Block.ControlHandler, args=(
            self.__Ctrl_Cmd_output, self.__Ctrl_Result_input, self.__Ctrl_State),)

        self.__Diag_Task = mprocess.Process(target=self.__Ctrl_Block.DiagHandler, args=(
            self.__Diag_Table_output, self.__Diag_Result_input, self.__Diag_State),)

        self.__Ctrl_Task.daemon = True
        self.__Ctrl_Task.start()

        self.__Diag_Task.daemon = True
        self.__Diag_Task.start()

        self.__InitGUI()

        print("Inicialización finalizada")

    def __InitGUI(self):
        '''!
        Reporta el estado
        '''
        Window = Tk()
        Window.title("PEATC APP")
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

        btn = Button(BtnFrame, text="Click Me", command=self.clicked)
        btn.place(bordermode=OUTSIDE, height=80, width=200, x=100, y=200)

        Window.mainloop()

    def clicked(self):
        print("Botton Hola Hola")
        self.btn["state"] = "disabled"
        self.btn["state"] = "normal"