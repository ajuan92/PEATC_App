import os
import sys
from time import time
from tkinter import *
from tkinter.ttk import Combobox
from tkinter import ttk
from tkinter import Label
from random import randint

from time import sleep
import struct

import multiprocessing as mprocess
from multiprocessing import Array
from multiprocessing import Value
from multiprocessing import Manager

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

CURR_PATH = os.path.dirname(os.path.realpath(__file__))
LOW_DRIVE_PATH = CURR_PATH + "\\..\\Control_Block"

sys.path.append(
    LOW_DRIVE_PATH)

from PEATC_Control import PEATC_Control

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
STATE_RESET = 11
STATE_INIT_TEST = 2
STATE_WAIT_RAW_DATA = 3
STATE_ANALYZE_DATA = 4
STATE_INIT_DIAGNOSTIC = 5
STATE_WAIT_DIAGNOSTIC = 6
STATE_SEND_RESULT = 7

State_Dict = {
    "STATE_STAND_BY": 0,
    "STATE_RESET": 11,
    "STATE_INIT_TEST": 2,
    "STATE_WAIT_RAW_DATA": 3,
    "STATE_ANALYZE_DATA": 4,
    "STATE_INIT_DIAGNOSTIC": 5,
    "STATE_WAIT_DIAGNOSTIC": 6,
    "STATE_SEND_RESULT": 7,
}


CONFIG_SignaldB = [30, 40, 50, 60]

CONFIG_Latency = [100, 233, 120, 54]
CONFIG_Freq = [50, 70, 100, 150]


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
        print('Inicio Manager')
        manager = Manager()
        print('Fin Manager')

        self.WaveData = manager.list()
        self.WaveData.append(
            dict({'SignaldB': 0, 'NewData': 0, 'Wave': [], 'FullSignal': []}))
        print(self.WaveData)

        for MemIndex in range(len(CONFIG_SignaldB)):
            Currd = self.WaveData[MemIndex]
            Currd['SignaldB'] = CONFIG_SignaldB[MemIndex]
            self.WaveData[MemIndex] = Currd

            if MemIndex is not len(CONFIG_SignaldB) - 1:
                self.WaveData.append(
                    {'SignaldB': 0, 'NewData': 0, 'Wave': [], 'FullSignal': []})

        print(self.WaveData)

        self.__Cmd_Template = Array('i', range(5))
        self.__Cmd_DiagAge = Array('i', range(2))

        self.GuiCurrState = STATE_STAND_BY
        self.GuiUpdateState = Value('i', STATE_STAND_BY)
        self.GuiPrevState = STATE_RESET

        self.Ctrl_Cmd_output, self.Ctrl_Cmd_input = mprocess.Pipe(False)
        self.Ctrl_Result_output, self.Ctrl_Result_input = mprocess.Pipe(
            False)

        self.Diag_Table_output, self.Diag_Table_input = mprocess.Pipe(
            False)
        self.Diag_Result_output, self.Diag_Result_input = mprocess.Pipe(
            False)

        self.Ctrl_State = Array('i', range(1))

        self.Diag_State = Array('i', range(1))

        Ctrl_Block = PEATC_Control()

        Ctrl_Task = mprocess.Process(target=Ctrl_Block.ControlHandler, args=(
            self.Ctrl_Cmd_output, self.Ctrl_Result_input, self.Ctrl_State),)

        Diag_Task = mprocess.Process(target=Ctrl_Block.DiagHandler, args=(
            self.Diag_Table_output, self.Diag_Result_input, self.Diag_State),)

        Ctrl_Task.daemon = True
        Ctrl_Task.start()

        Diag_Task.daemon = True
        Diag_Task.start()

        Gui_Task = mprocess.Process(target=self.GuiCom)

        Gui_Task.daemon = True
        Gui_Task.start()

        self.InitGUI()

        print("Inicialización finalizada")
        print(self.GuiCurrState)

    def InitGUI(self):
        '''!
        Reporta el estado
        '''
        self.Window = Tk()
        self.Window.title("PEATC APP")
        self.Window.geometry("1000x600")

        self.__ConfParam()

        self.BtnFrame = Frame(self.Window)
        self.BtnFrame.pack(fill="both", side="right", expand=1)
        self.BtnFrame.config(bg="white")
        self.BtnFrame.config(width="400", height="400")

        self.Label_State = Label(self.BtnFrame, text="STATE_STAND_BY")
        self.Label_State.place(x=100, y=50)
        self.Label_State.config(bg="white")
        #self.Label_State.after(1000, self.__UpdateStateLabel)

        self.GrafFrame = Frame(self.Window)
        self.GrafFrame.pack(fill="both", side="left", expand=1)
        self.GrafFrame.config(bg="white")
        self.GrafFrame.config(width="600", height="400")

        self.Graf_Notebook = ttk.Notebook(
            self.GrafFrame, width="600", height="400")
        self.Graf_Notebook.place(x=10, y=1)
        self.GrafTab = ttk.Frame(self.Graf_Notebook)
        self.WaveTab = ttk.Frame(self.Graf_Notebook)
        self.Graf_Notebook.add(self.GrafTab, text='First')
        self.Graf_Notebook.add(self.WaveTab, text='Second')
        self.Graf_Notebook.pack(fill='both', expand=True)

        self.__ConfBottons()

        self.fig = Figure(figsize=(5, 5), dpi=100)

        self.canvas = FigureCanvasTkAgg(self.fig, self.GrafTab)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)
        self.GrafTab.after(1000, self.__UpdateData)

        self.Window.mainloop()

    def __UpdateData(self):

        # print(self.WaveData[0])
        GrafData = self.WaveData[0]['FullSignal']
        # print(GrafData)
        self.fig.clear()
        self.fig.add_subplot(1, 1, 1).plot(
            list(range(0, len(GrafData))), GrafData)
        self.fig.tight_layout()
        self.canvas.draw()

        self.GrafTab.after(1000, self.__UpdateData)

    def __UpdateStateLabel(self):

        # print(self.GuiCurrState)
        for key, value in State_Dict.items():
            if self.GuiUpdateState.value is value:
                NewState = StringVar()
                NewState.set(key)
                self.Label_State.config(textvariable=NewState)

        self.Label_State.after(1000, self.__UpdateStateLabel)

    def __ConfParam(self):

        ConfParamFrame = Frame(self.Window)
        ConfParamFrame.pack(fill="both", side="bottom", expand=1)
        ConfParamFrame.config(bg="white")
        ConfParamFrame.config(width="600", height="50")

        Label_SignaldB = Label(ConfParamFrame, text="SignaldB")
        Label_SignaldB.place(x=100, y=50)
        Label_SignaldB.config(bg="white")
        self.Entry_SignaldB = ttk.Combobox(
            ConfParamFrame, width=5, state='readonly')
        self.Entry_SignaldB.place(x=100, y=70)
        self.Entry_SignaldB['values'] = CONFIG_SignaldB
        self.Entry_SignaldB.current(0)

        Label_Latency = Label(ConfParamFrame, text="Latency")
        Label_Latency.place(x=200, y=50)
        Label_Latency.config(bg="white")
        self.Entry_Latency = ttk.Combobox(
            ConfParamFrame, width=5, state='readonly')
        self.Entry_Latency.place(x=200, y=70)
        self.Entry_Latency['values'] = CONFIG_Latency
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
        self.Entry_Freq['values'] = CONFIG_Freq
        self.Entry_Freq.current(0)

        Label_Age = Label(ConfParamFrame, text="Age")
        Label_Age.place(x=500, y=50)
        Label_Age.config(bg="white")
        self.Entry_Age = ttk.Combobox(
            ConfParamFrame, width=5, state='readonly')
        self.Entry_Age.place(x=500, y=70)
        self.Entry_Age['values'] = list(range(0, 100))
        self.Entry_Age.current(0)

    def __ConfBottons(self):

        btnGenSignal = Button(self.BtnFrame, text="Get PEATC",
                              command=self.__GenSignalBotton)
        btnGenSignal.place(bordermode=OUTSIDE, height=80,
                           width=200, x=100, y=100)

        btnDiagSignal = Button(self.BtnFrame, text="Diagnostic",
                               command=self.__GenDiagBotton)
        btnDiagSignal.place(bordermode=OUTSIDE, height=80,
                            width=200, x=100, y=300)

    def __GenSignalBotton(self):

        if self.GuiCurrState is STATE_STAND_BY:
            print("Inicio Click")
            sys.stdout.flush()
            self.__Cmd_Template[0] = 1
            self.__Cmd_Template[1] = int(self.Entry_SignaldB.get())
            self.__Cmd_Template[2] = int(self.Entry_Latency.get())
            self.__Cmd_Template[3] = int(self.Entry_Polarity.get())
            self.__Cmd_Template[4] = int(self.Entry_Freq.get())

    def __GenDiagBotton(self):

        if self.GuiCurrState is STATE_STAND_BY:
            print("Inicio Click DiagBotton")
            sys.stdout.flush()
            self.__Cmd_DiagAge[0] = 1
            self.__Cmd_DiagAge[1] = int(self.Entry_Age.get())
        else:
            print("Inicio Click Disable")
            sys.stdout.flush()

    def GuiCom(self):

        print("Inicio Tarea de Comunicación")
        sys.stdout.flush()

        while True:

            if self.GuiPrevState is not self.GuiCurrState:
                self.GuiUpdateState.value = self.GuiCurrState
                self.GuiPrevState = self.GuiCurrState
                print(self.GuiUpdateState.value)
                sys.stdout.flush()

            if self.GuiCurrState is STATE_STAND_BY:

                if self.__Cmd_Template[0] is 1:
                    print("Read PEATC")
                    self.GuiCurrState = STATE_INIT_TEST
                elif self.__Cmd_DiagAge[0] is 1:
                    self.GuiCurrState = STATE_INIT_DIAGNOSTIC

            elif self.GuiCurrState is STATE_INIT_TEST:

                Cmd_Template["Cmd"] = self.__Cmd_Template[0]
                Cmd_Template["Gs_SignaldB"] = self.__Cmd_Template[1]
                Cmd_Template["Gs_Latency"] = self.__Cmd_Template[2]
                Cmd_Template["Gs_Polarity"] = self.__Cmd_Template[3]
                Cmd_Template["Gs_Freq"] = self.__Cmd_Template[4]

                CtrlCurrState = self.Ctrl_State[0]

                if CtrlCurrState == 0:
                    print("Envio Conf")
                    self.Ctrl_Cmd_input.send(Cmd_Template)
                    self.__Cmd_Template[0] = 0
                    print("Fin Conf")
                    self.GuiCurrState = STATE_WAIT_RAW_DATA
                    print("Waiting Result...")
                else:
                    self.GuiCurrState = STATE_STAND_BY
                    print("Return Stand By")

            elif self.GuiCurrState is STATE_WAIT_RAW_DATA:

                CtrlCurrState = self.Ctrl_State[0]

                if CtrlCurrState is 0:
                    self.GuiCurrState = STATE_ANALYZE_DATA

            elif self.GuiCurrState is STATE_ANALYZE_DATA:

                print("Inicio Reciv Result")
                WavePEATC1, FullWaveData1 = self.Ctrl_Result_output.recv()
                print("Fin Reciv Result")
                print("---------")
                print(WavePEATC1)
                print(FullWaveData1)
                print(Cmd_Template["Gs_SignaldB"])

                for i, dic in enumerate(self.WaveData):
                    if dic['SignaldB'] == Cmd_Template["Gs_SignaldB"]:
                        GetPEATCDict = self.WaveData[i]
                        GetPEATCDict['NewData'] = 1
                        GetPEATCDict['Wave'] = WavePEATC1
                        GetPEATCDict['FullSignal'] = FullWaveData1
                        self.WaveData[i] = GetPEATCDict

                print("---------")

                print(self.WaveData)
                self.GuiCurrState = STATE_STAND_BY

            elif self.GuiCurrState is STATE_INIT_DIAGNOSTIC:

                self.WaveTable = []

                DiagCurrState = self.Diag_State[0]

                if DiagCurrState == 0:
                    # Cuantas señales SON NECESARIAS, TODAS? Hay limites?
                    for i, dic in enumerate(self.WaveData):
                        if dic['NewData'] == 1:
                            self.WaveTable.append(self.WaveData[i]['Wave'])

                    print(self.WaveTable)
                    DiagMatrix = [self.__Cmd_DiagAge[1], self.WaveTable]

                    print("Envio Diag")
                    self.Diag_Table_input.send(DiagMatrix)
                    self.__Cmd_DiagAge[0] = 0
                    print("Fin Envio Diag")

                    self.GuiCurrState = STATE_WAIT_DIAGNOSTIC
                    print("Waiting Diag Result...")
                    sys.stdout.flush()
                else:
                    self.GuiCurrState = STATE_STAND_BY
                    print("Return Stand By")
                    sys.stdout.flush()

            elif self.GuiCurrState is STATE_WAIT_RAW_DATA:

                DiagCurrState = self.Ctrl_State[0]

                if DiagCurrState is 0:
                    self.GuiCurrState = STATE_SEND_RESULT

            elif self.GuiCurrState is STATE_SEND_RESULT:

                print("Inicio Reciv Result")
                DiagnPEATC = self.Diag_Result_output.recv()
                print("Fin Reciv Result")
                print(DiagnPEATC)
                print("---------")
                sys.stdout.flush()
                self.GuiCurrState = STATE_STAND_BY
                print(self.GuiCurrState)
                print("---------")
