import os
import sys
from time import time
from tkinter import *
from tkinter.ttk import Combobox
from tkinter import ttk
from tkinter import Label

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

        self.__Cmd_Template = {
            "Cmd": 0,
            "Gs_SignaldB": 0,
            "Gs_Latency": 0,
            "Gs_Polarity": 0,
            "Gs_Freq": 0,
        }

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

        self.__Gui_Task = mprocess.Process(target=self.GuiCom)

        self.__Ctrl_Task.daemon = True
        self.__Ctrl_Task.start()

        self.__Diag_Task.daemon = True
        self.__Diag_Task.start()

        self.__Gui_Task.daemon = True
        self.__Gui_Task.start()

        self.__InitGUI()

        print("Inicialización finalizada")

    def __InitGUI(self):
        '''!
        Reporta el estado
        '''
        Window = Tk()
        Window.title("PEATC APP")
        Window.geometry("1000x600")

        #------------
        self.__ConfParam(Window)
        #------------

        BtnFrame = Frame(Window)
        BtnFrame.pack(fill="both", side="right", expand=1)
        BtnFrame.config(bg="white")
        BtnFrame.config(width="400", height="400")

        GrafFrame = Frame(Window)
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

        btn = Button(BtnFrame, text="Click Me", command=self.__clicked)
        btn.place(bordermode=OUTSIDE, height=80, width=200, x=100, y=200)

        Window.mainloop()

    def __ConfParam(self, Window):

        ConfParamFrame = Frame(Window)
        ConfParamFrame.pack(fill="both", side="bottom", expand=1)
        ConfParamFrame.config(bg="white")
        ConfParamFrame.config(width="600", height="50")

        Label_SignaldB = Label(ConfParamFrame, text="SignaldB")
        Label_SignaldB.place(x=100, y=50)
        Label_SignaldB.config(bg="white")
        self.Entry_SignaldB = ttk.Combobox(
            ConfParamFrame, width=5, state='readonly')
        self.Entry_SignaldB.place(x=100, y=70)
        self.Entry_SignaldB['values'] = [30, 40, 50, 60]
        self.Entry_SignaldB.current(0)

        Label_Latency = Label(ConfParamFrame, text="Latency")
        Label_Latency.place(x=200, y=50)
        Label_Latency.config(bg="white")
        self.Entry_Latency = ttk.Combobox(
            ConfParamFrame, width=5, state='readonly')
        self.Entry_Latency.place(x=200, y=70)
        self.Entry_Latency['values'] = [100, 233, 120, 54]
        self.Entry_Latency.current(0)

        Label_Polarity = Label(ConfParamFrame, text="Polarity")
        Label_Polarity.place(x=300, y=50)
        Label_Polarity.config(bg="white")
        self.Entry_Polarity = ttk.Combobox(
            ConfParamFrame, width=5, state='readonly')
        self.Entry_Polarity.place(x=300, y=70)
        self.Entry_Polarity['values'] = [1, 0]
        self.Entry_Polarity.current(0)

        Label_Freq = Label(ConfParamFrame, text="Freq")
        Label_Freq.place(x=400, y=50)
        Label_Freq.config(bg="white")
        self.Entry_Freq = ttk.Combobox(
            ConfParamFrame, width=5, state='readonly')
        self.Entry_Freq.place(x=400, y=70)
        self.Entry_Freq['values'] = [50, 70, 100, 150]
        self.Entry_Freq.current(0)

    def __clicked(self):
        print("Inicio Click")
        self.__Cmd_Template["Cmd"] = 1
        self.__Cmd_Template["Gs_SignaldB"] = self.Entry_SignaldB.get()
        self.__Cmd_Template["Gs_Latency"] = self.Entry_Latency.get()
        self.__Cmd_Template["Gs_Polarity"] = self.Entry_Polarity.get()
        self.__Cmd_Template["Gs_Freq"] = self.Entry_Freq.get()

    def GuiCom(self):

        print("Inicio Tarea de Comunicación")
        sys.stdout.flush()

        GuiCurrState = 0

        while True:

            if GuiCurrState is 0:

                if self.__Cmd_Template["Cmd"] is 1:

                    CtrlCurrState = self.__Ctrl_State[0]
                    print(CtrlCurrState)

                    if CtrlCurrState == 0:
                        print("Envio Conf")
                        self.__Ctrl_Cmd_input.send(self.__Cmd_Template)
                        self.__Cmd_Template["Cmd"] = 0
                        print("Fin Conf")
                        GuiCurrState = 1

            elif GuiCurrState is 1:

                CtrlCurrState = self.__Ctrl_State[0]
                print(CtrlCurrState)

                if CtrlCurrState is 0:
                    GuiCurrState = 2

            elif GuiCurrState is 2:

                print("Inicio Reciv Result")
                WavePEATC1, FullWaveData1 = self.__Ctrl_Result_output.recv()
                print("Fin Reciv Result")
                print("---------")
                print(WavePEATC1)
                print(FullWaveData1)
                print("---------")

                GuiCurrState = 0
