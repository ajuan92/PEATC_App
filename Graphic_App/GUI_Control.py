import os
import sys
import csv
from datetime import datetime

from tkinter import *
from tkinter import ttk
from tkinter import Label
import tkinter as tk

import multiprocessing as mprocess
from multiprocessing import Array
from multiprocessing import Value
from multiprocessing import Manager

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

CURR_PATH = os.path.dirname(os.path.realpath(__file__))
APP_LOGS_PATH = CURR_PATH + "\\..\\_Logs\\"
LOW_DRIVE_PATH = CURR_PATH + "\\..\\Control_Block"

sys.path.append(
    LOW_DRIVE_PATH)

from PEATC_Control import PEATC_Control
from PEATC_Control import PEATC_Ctrl_Cmd_Dict
from PEATC_Control import PEATC_CONTROL_CMD_START_TEST
from PEATC_Control import*

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
STATE_CREATING_LOG = 8

State_Dict = {
    "     STATE_STAND_BY    ": 0,
    "      STATE_RESET      ": 11,
    "    STATE_INIT_TEST    ": 2,
    "  STATE_WAIT_RAW_DATA  ": 3,
    "   STATE_ANALYZE_DATA  ": 4,
    " STATE_INIT_DIAGNOSTIC ": 5,
    " STATE_WAIT_DIAGNOSTIC ": 6,
    "   STATE_SEND_RESULT   ": 7,
    "  STATE_CREATING_LOG   ": 8,
}

Diag_Dict = {
    "Normal values": 0,
    "Prolonged latency \nin Wave I": 1,
    "Prolonged latency \nbetween peaks I-III": 2,
    "Prolonged latency \nbetween peaks III-V": 3,
    "Prolonged latency \nbetween peaks IV-V and III-V ": 4,
    "Wave III absent with \npresence of I and V": 5,
    "Wave V absent with \npresence of I and III": 6,
    "Wave V absent with \nnormal of I and III": 7,
    "Absence of waves": 8,
    "Excess in amplitude \nradius V / I": 9,
    "Absence of waves \nexcept I (and possibly II)": 10,
    "No Diagnostic": 11
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
        print("Inicialización PEATC App")
        manager = Manager()

        self.WaveData = manager.list()
        self.WaveData.append(
            dict({'SignaldB': 0, 'NewData': 0, 'Wave': [], 'FullSignal': []}))

        for MemIndex in range(len(CONFIG_SignaldB)):
            Currd = self.WaveData[MemIndex]
            Currd['SignaldB'] = CONFIG_SignaldB[MemIndex]
            self.WaveData[MemIndex] = Currd

            if MemIndex is not len(CONFIG_SignaldB) - 1:
                self.WaveData.append(
                    {'SignaldB': 0, 'NewData': 0, 'Wave': [], 'FullSignal': []})

        self.ArrNewData = Array('i', len(CONFIG_SignaldB))

        self.__Cmd_Template = Array('i', range(5))
        self.__Cmd_DiagAge = Array('i', range(3))
        self.__Cmd_LogName = Array('c', range(50))
        self.__Cmd_Reset = Array('i', range(4))

        for i in range(len(self.__Cmd_Reset)):
            self.__Cmd_Reset[i] = 0

        self.GuiCurrState = STATE_STAND_BY
        self.GuiUpdateState = Value('i', STATE_STAND_BY)
        self.GuiPrevState = STATE_RESET

        self.GuiUpdateDiag = Value('i', Diag_Dict["No Diagnostic"])

        self.Ctrl_Cmd_output, self.Ctrl_Cmd_input = mprocess.Pipe(False)
        self.Ctrl_Result_output, self.Ctrl_Result_input = mprocess.Pipe(
            False)

        self.Diag_Table_output, self.Diag_Table_input = mprocess.Pipe(
            False)
        self.Diag_Result_output, self.Diag_Result_input = mprocess.Pipe(
            False)

        self.Ctrl_State = Value('i', PEATC_CONTROL_STATE_STAND_BY)

        self.Diag_State = Value('i', PEATC_CONTROL_STATE_STAND_BY)

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

        print("Inicialización PEATC App finalizada")

        self.InitGUI()

    def InitGUI(self):
        '''!
        Reporta el estado
        '''
        self.Window = Tk()
        self.Window.title("PEATC APP")
        self.Window.columnconfigure((0, 1, 2), minsize=1)

        self.BtnFrame = Frame(self.Window)
        self.BtnFrame.grid(row=0, column=2)
        self.BtnFrame.config(bg="white", bd=1, relief=GROOVE)
        self.BtnFrame.config(width="400", height="1000")

        self.GrafTab = Frame(self.Window)
        self.GrafTab.grid(row=0, column=0)
        self.GrafTab.config(bg="white")
        self.GrafTab.config(width="600", height="1000")

        self.MiddleWindow = Frame(self.Window)
        self.MiddleWindow.grid(row=0, column=1)
        self.MiddleWindow.rowconfigure((0, 1, 2), minsize=1)
        self.MiddleWindow.rowconfigure(0, minsize=200)

        self.WaveTab = Frame(self.MiddleWindow)
        self.WaveTab.grid(row=0, column=0, sticky=NE + NW)
        self.WaveTab.config(bg="white")
        self.WaveTab.config(width="600", height="600")

        self.ConfParamFrame = Frame(self.MiddleWindow)
        self.ConfParamFrame.grid(row=1, column=0, sticky=E + W)
        self.ConfParamFrame.config(bg="white", bd=1, relief=GROOVE)
        self.ConfParamFrame.config(width="720", height="200")

        self.CurrTextLogFileIndex = 0
        self.PrevTextLogFileIndex = 0
        self.text = Text(self.MiddleWindow, wrap="word", height=20, width=89)
        self.text.grid(row=2, column=0, sticky=SE + SW)
        self.text.tag_configure("stderr", foreground="white")
        self.text.after(100, self.__UpdateLog)

        self.__ConfParam()
        self.__ConfBottons()
        self.__ConfWaveTab()
        self.__ConfWaveGraf()

        self.Window.mainloop()

    def __UpdateLog(self):

        with open('Tut20_Output.txt') as f:
            f.seek(self.CurrTextLogFileIndex)
            newText = f.read()
            self.PrevTextLogFileIndex = f.tell()

            if self.PrevTextLogFileIndex > self.CurrTextLogFileIndex:
                self.CurrTextLogFileIndex = self.PrevTextLogFileIndex
                self.text.insert(tk.END, newText)
                self.text.see("end")

            if self.__Cmd_Reset[3] is 1:
                self.text.delete('1.0', tk.END)
                self.__Cmd_Reset[3] = 0

        self.text.after(100, self.__UpdateLog)

    def __ConfWaveTab(self):

        WAVETAB_WIDTH = 70

        self.WaveTable = ttk.Treeview(self.WaveTab)
        self.WaveTable['columns'] = (
            "dB", "I A", "II A", "III A", "IV A", "V A",
            "I L", "II L", "III L", "IV L", "V L")
        self.WaveTable.column("#0", width=0, stretch=NO)
        self.WaveTable.column("dB", anchor=CENTER, width=WAVETAB_WIDTH)
        self.WaveTable.column("I A", anchor=CENTER, width=WAVETAB_WIDTH)
        self.WaveTable.column("II A", anchor=CENTER, width=WAVETAB_WIDTH)
        self.WaveTable.column("III A", anchor=CENTER, width=WAVETAB_WIDTH)
        self.WaveTable.column("IV A", anchor=CENTER, width=WAVETAB_WIDTH)
        self.WaveTable.column("V A", anchor=CENTER, width=WAVETAB_WIDTH)
        self.WaveTable.column("I L", anchor=CENTER, width=WAVETAB_WIDTH)
        self.WaveTable.column("II L", anchor=CENTER, width=WAVETAB_WIDTH)
        self.WaveTable.column("III L", anchor=CENTER, width=WAVETAB_WIDTH)
        self.WaveTable.column("IV L", anchor=CENTER, width=WAVETAB_WIDTH)
        self.WaveTable.column("V L", anchor=CENTER, width=WAVETAB_WIDTH)

        self.WaveTable.grid(row=0, column=0, columnspan=1)
        self.WaveTable.heading("#1", text="dB", anchor=CENTER)
        self.WaveTable.heading("#2", text="I Amp", anchor=CENTER)
        self.WaveTable.heading("#3", text="II Amp", anchor=CENTER)
        self.WaveTable.heading("#4", text="III Amp", anchor=CENTER)
        self.WaveTable.heading("#5", text="IV Amp", anchor=CENTER)
        self.WaveTable.heading("#6", text="V  Amp", anchor=CENTER)
        self.WaveTable.heading("#7", text="I Lat", anchor=CENTER)
        self.WaveTable.heading("#8", text="II Lat", anchor=CENTER)
        self.WaveTable.heading("#9", text="III Lat", anchor=CENTER)
        self.WaveTable.heading("#10", text="IV Lat", anchor=CENTER)
        self.WaveTable.heading("#11", text="V  Lat", anchor=CENTER)

        for i in range(len(CONFIG_SignaldB)):
            self.WaveTable.insert(parent='', index=i, iid=i, values=([]))

        self.WaveTable.config(height="20")
        self.WaveTab.after(1000, self.__UpdateTable)

    def __ReSizeWaveGraf(self, GrafNum):
        self.canvas.configure(scrollregion=(
            0, 0, 0, 400 * (GrafNum)), width=600, height=1000)

    def __ConfWaveGraf(self):

        self.PrevReadyGraf = 0

        self.canvas = Canvas(self.GrafTab)
        self.graframe = Frame(self.canvas)

        self.yScrollbar = Scrollbar(
            self.GrafTab, orient="vertical", command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.yScrollbar.set)
        self.yScrollbar.pack(side="right", fill="y")

        self.canvas.pack(side="left", expand=True, fill="both")
        self.canvas.create_window((0, 0), window=self.graframe, anchor='nw')
        self.graframe.bind("<Configure>", self.__ReSizeWaveGraf(1))

        self.GrafTab.after(1000, self.__UpdateData())

    def __ConfParam(self):

        Label_SignaldB = Label(self.ConfParamFrame, text="SignaldB")
        Label_SignaldB.place(x=100, y=50)
        Label_SignaldB.config(bg="white")
        self.Entry_SignaldB = ttk.Combobox(
            self.ConfParamFrame, width=5, state='readonly')
        self.Entry_SignaldB.place(x=100, y=70)
        self.Entry_SignaldB['values'] = CONFIG_SignaldB
        self.Entry_SignaldB.current(0)

        Label_Latency = Label(self.ConfParamFrame, text="Latency")
        Label_Latency.place(x=200, y=50)
        Label_Latency.config(bg="white")
        self.Entry_Latency = ttk.Combobox(
            self.ConfParamFrame, width=5, state='readonly')
        self.Entry_Latency.place(x=200, y=70)
        self.Entry_Latency['values'] = CONFIG_Latency
        self.Entry_Latency.current(0)

        Label_Polarity = Label(self.ConfParamFrame, text="Polarity")
        Label_Polarity.place(x=300, y=50)
        Label_Polarity.config(bg="white")
        self.Entry_Polarity = ttk.Combobox(
            self.ConfParamFrame, width=5, state='readonly')
        self.Entry_Polarity.place(x=300, y=70)
        self.Entry_Polarity['values'] = [1, 0]
        self.Entry_Polarity.current(0)

        Label_Freq = Label(self.ConfParamFrame, text="Freq")
        Label_Freq.place(x=400, y=50)
        Label_Freq.config(bg="white")
        self.Entry_Freq = ttk.Combobox(
            self.ConfParamFrame, width=5, state='readonly')
        self.Entry_Freq.place(x=400, y=70)
        self.Entry_Freq['values'] = CONFIG_Freq
        self.Entry_Freq.current(0)

        Label_Age = Label(self.ConfParamFrame, text="Age")
        Label_Age.place(x=500, y=50)
        Label_Age.config(bg="white")
        self.Entry_Age = ttk.Combobox(
            self.ConfParamFrame, width=5, state='readonly')
        self.Entry_Age.place(x=500, y=70)
        self.Entry_Age['values'] = list(range(0, 100))
        self.Entry_Age.current(0)

        Label_TexName = Label(self.ConfParamFrame, text="Log Name")
        Label_TexName.place(x=230, y=120)
        Label_TexName.config(bg="white")
        self.PeatcTextLogName = Text(
            self.ConfParamFrame, wrap="word", height=1, width=30)
        self.PeatcTextLogName.place(x=300, y=120)
        self.PeatcTextLogName.tag_configure("stderr", foreground="white")
        self.PeatcTextLogName.insert("1.0", "New_PEATC_Test")

    def __ConfBottons(self):

        self.Label_State = Label(self.BtnFrame, text="STATE_STAND_BY")
        self.Label_State.config(anchor=CENTER)
        self.Label_State.place(x=130, y=50)
        self.Label_State.config(bg="white")
        self.Label_State.after(1000, self.__UpdateStateLabel)

        btnGenSignal = Button(self.BtnFrame, text="Get PEATC",
                              command=self.__GenSignalBotton)
        btnGenSignal.place(bordermode=OUTSIDE, height=80,
                           width=200, x=100, y=100)

        btnDiagSignal = Button(self.BtnFrame, text="Diagnostic",
                               command=self.__GenDiagBotton)
        btnDiagSignal.place(bordermode=OUTSIDE, height=80,
                            width=200, x=100, y=300)

        btnReset = Button(self.BtnFrame, text="Reset",
                          command=self.__GenResetBotton)
        btnReset.place(bordermode=OUTSIDE, height=80,
                       width=200, x=100, y=500)

        self.Label_Diag = Label(self.BtnFrame, text="No Diagnostic")
        self.Label_Diag.config(anchor=CENTER)
        self.Label_Diag.place(x=130, y=700)
        self.Label_Diag.config(bg="white")
        self.Label_Diag.after(1000, self.__UpdateDiagLabel)

    def __UpdateTable(self):

        WaveRead = []
        dBRead = []
        ReadyWave = 0

        for i, dic in enumerate(self.WaveData):
            if dic['NewData'] == 1:
                WaveRead.append(self.WaveData[i]['Wave'])
                dBRead.append(self.WaveData[i]['SignaldB'])
                ReadyWave = ReadyWave + 1

        if self.__Cmd_Reset[1] is 0:
            for i in range(ReadyWave):
                self.WaveTable.item(str(i), values=(
                    dBRead[i], WaveRead[i][0][0], WaveRead[i][1][0],
                    WaveRead[i][2][0], WaveRead[i][3][0], WaveRead[i][4][0],
                    WaveRead[i][0][1], WaveRead[i][1][1], WaveRead[i][2][1],
                    WaveRead[i][3][1], WaveRead[i][4][1]))
        else:
            for i in range(len(self.WaveTable.get_children())):
                self.WaveTable.item(str(i), values=(
                    [], [], [], [], [], [],
                    [], [], [], [], []))
            self.__Cmd_Reset[1] = 0

        self.WaveTab.after(1000, self.__UpdateTable)

    def __UpdateData(self):

        GrafData = []
        ReadyGraf = 0

        if self.__Cmd_Reset[2] is 1:
            self.PrevReadyGraf = 0

            print(self.graframe.winfo_children())
            for widget in self.graframe.winfo_children():
                widget.destroy()

            self.__Cmd_Reset[2] = 0

        for i, dic in enumerate(self.WaveData):
            if dic['NewData'] == 1:

                GrafData.append(self.WaveData[i]['FullSignal'])
                self.WaveData[i].update({'NewData': 0})
                ReadyGraf = ReadyGraf + 1

                if self.PrevReadyGraf < ReadyGraf:
                    self.PrevReadyGraf = ReadyGraf
                    self.graframe.bind(
                        "<Configure>", self.__ReSizeWaveGraf(ReadyGraf))

                if self.ArrNewData[i] == 1:
                    fig = Figure(figsize=(6, 4), dpi=100)

                    ax = fig.add_subplot(111)
                    ax.set_title('SignaldB' + ' ' + ''.join
                                 (str(self.WaveData[i]['SignaldB'])))
                    ax.set_xlabel('Time ms')
                    ax.set_ylabel('Voltage uV')
                    ax.plot(range(0, len(GrafData[0])), GrafData[0])

                    canvasAgg = FigureCanvasTkAgg(fig, self.graframe)
                    canvasAgg.get_tk_widget().grid(row=i, column=0)
                    canvasAgg.draw()

                    self.ArrNewData[i] = 0

        self.GrafTab.after(1000, self.__UpdateData)

    def __UpdateStateLabel(self):

        for key, value in State_Dict.items():
            if self.GuiUpdateState.value is value:
                NewState = StringVar()
                NewState.set(key)
                self.Label_State.config(textvariable=NewState)

        self.Label_State.after(1000, self.__UpdateStateLabel)

    def __UpdateDiagLabel(self):

        for key, value in Diag_Dict.items():
            if self.GuiUpdateDiag.value is value:
                NewState = StringVar()
                NewState.set(key)
                self.Label_Diag.config(textvariable=NewState)

        self.Label_Diag.after(1000, self.__UpdateDiagLabel)

    def __GenSignalBotton(self):

        if self.GuiCurrState is STATE_STAND_BY:
            print("> Comando inicio de prueba de PEATC")
            sys.stdout.flush()
            self.__Cmd_Template[0] = PEATC_CONTROL_CMD_START_TEST
            self.__Cmd_Template[1] = int(self.Entry_SignaldB.get())
            self.__Cmd_Template[2] = int(self.Entry_Latency.get())
            self.__Cmd_Template[3] = int(self.Entry_Polarity.get())
            self.__Cmd_Template[4] = int(self.Entry_Freq.get())
        else:
            print("> Actualmente existe una operación en progreso")

    def __GenDiagBotton(self):

        if self.GuiCurrState is STATE_STAND_BY:
            print("> Comando diagnostico de señales PEATC")
            sys.stdout.flush()
            self.__Cmd_DiagAge[0] = 1
            self.__Cmd_DiagAge[1] = int(self.Entry_Age.get())

            LogString = self.PeatcTextLogName.get(
                "1.0", "end-1c")[:len(self.__Cmd_LogName)]

            self.__Cmd_DiagAge[2] = len(LogString)

            for x in (range(len(self.__Cmd_LogName) - 1)):
                self.__Cmd_LogName[x] = bytes(" ", "utf-8")

            for x in (range(len(LogString) - 1)):
                self.__Cmd_LogName[x] = bytes(LogString[x], "utf-8")
        else:
            print("> Actualmente existe una operación en progreso")

        sys.stdout.flush()

    def __GenResetBotton(self):

        if self.GuiCurrState is STATE_STAND_BY:
            print("> Comando reset datos de prueba PEATC")
            self.__Cmd_Reset[0] = 1
            self.__Cmd_Reset[1] = 1
            self.__Cmd_Reset[2] = 1
            self.__Cmd_Reset[3] = 1
        else:
            print("> Actualmente existe una operación en progreso")
        sys.stdout.flush()

    def __StateVal2key(self, SearchVal, BaseDict):
        for key, value in BaseDict.items():
            if SearchVal is value:
                return key

    def GuiCom(self):

        print("> Inicio Modulo PEATC GUI")
        sys.stdout.flush()

        while True:

            if self.GuiPrevState is not self.GuiCurrState:
                # print("\n-----------------Estado--------------------")
                # print("-Estado previo: \n" +
                #      str(self.__StateVal2key(self.GuiPrevState)))
                # print("-Estado actual: \n " +
                #      str(self.__StateVal2key(self.GuiCurrState)))
                # print("-------------------------------------------")

                sys.stdout.flush()
                self.GuiUpdateState.value = self.GuiCurrState
                self.GuiPrevState = self.GuiCurrState

            if self.GuiCurrState is STATE_STAND_BY:

                if self.__Cmd_Template[0] is PEATC_CONTROL_CMD_START_TEST:
                    print("> Read PEATC")
                    self.GuiCurrState = STATE_INIT_TEST
                elif self.__Cmd_DiagAge[0] is 1:
                    print("> Run Diag PEATC")
                    self.GuiCurrState = STATE_INIT_DIAGNOSTIC
                elif self.__Cmd_Reset[0] is 1:
                    self.GuiCurrState = STATE_RESET
                else:
                    self.GuiCurrState = STATE_STAND_BY
                sys.stdout.flush()

            if self.GuiCurrState is STATE_INIT_TEST:

                PEATC_Ctrl_Cmd_Dict["Cmd"] = self.__Cmd_Template[0]
                PEATC_Ctrl_Cmd_Dict["Gs_SignaldB"] = self.__Cmd_Template[1]
                PEATC_Ctrl_Cmd_Dict["Gs_Latency"] = self.__Cmd_Template[2]
                PEATC_Ctrl_Cmd_Dict["Gs_Polarity"] = self.__Cmd_Template[3]
                PEATC_Ctrl_Cmd_Dict["Gs_Freq"] = self.__Cmd_Template[4]

                CtrlCurrState = self.Ctrl_State.value

                if CtrlCurrState == PEATC_CONTROL_STATE_STAND_BY:
                    print("Envio Cmd a PEATC_Ctrl")
                    self.Ctrl_Cmd_input.send(PEATC_Ctrl_Cmd_Dict)
                    self.__Cmd_Template[0] = PEATC_CONTROL_CMD_STOP_TEST
                    self.GuiCurrState = STATE_WAIT_RAW_DATA
                    print("Waiting Result...")
                else:
                    self.GuiCurrState = STATE_STAND_BY
                    print("PEATC_Ctrl no disponible regreso a Stand By")

            elif self.GuiCurrState is STATE_WAIT_RAW_DATA:

                CtrlCurrState = self.Ctrl_State.value
                print("Waiting Result PEATC_Ctrl in state " +
                      PEATC_Ctrl_State_Dict[CtrlCurrState])

                if CtrlCurrState is PEATC_CONTROL_STATE_STAND_BY:
                    self.GuiCurrState = STATE_ANALYZE_DATA

            elif self.GuiCurrState is STATE_ANALYZE_DATA:

                print("\n> Se recibe resultado de PEATC_Ctrl")
                WavePEATC1, FullWaveData1 = self.Ctrl_Result_output.recv()
                print("----Wave Amp & Lat----")
                print(WavePEATC1)
                print("-----Full Wave Data----")
                print(FullWaveData1)
                print("\n>Save SignaldB " +
                      str(PEATC_Ctrl_Cmd_Dict["Gs_SignaldB"]))

                for i, dic in enumerate(self.WaveData):
                    if dic['SignaldB'] == PEATC_Ctrl_Cmd_Dict["Gs_SignaldB"]:
                        GetPEATCDict = self.WaveData[i]
                        GetPEATCDict['NewData'] = 1
                        GetPEATCDict['Wave'] = WavePEATC1
                        GetPEATCDict['FullSignal'] = FullWaveData1
                        self.WaveData[i] = GetPEATCDict
                        self.ArrNewData[i] = 1
                        CurrWaveIndex = i

                print(self.WaveData[CurrWaveIndex])
                print("-----------------------\n")
                self.GuiCurrState = STATE_STAND_BY

            elif self.GuiCurrState is STATE_INIT_DIAGNOSTIC:

                self.WaveTable = []

                DiagCurrState = self.Diag_State.value

                if DiagCurrState == 0:
                    # Cuantas señales SON NECESARIAS, TODAS? Hay limites?
                    for i, dic in enumerate(self.WaveData):
                        if dic['NewData'] == 1:
                            self.WaveTable.append(self.WaveData[i]['Wave'])

                    print("----Wave Amp & Lat----")
                    print(self.WaveTable)
                    DiagMatrix = [self.__Cmd_DiagAge[1], self.WaveTable]

                    print("Envio señal de PEATC para diagnostico")
                    self.Diag_Table_input.send(DiagMatrix)
                    self.__Cmd_DiagAge[0] = 0

                    self.GuiCurrState = STATE_WAIT_DIAGNOSTIC
                    print("Waiting Diag Result...")
                    sys.stdout.flush()
                else:
                    self.GuiCurrState = STATE_STAND_BY
                    print("Return Stand By")
                    sys.stdout.flush()

            elif self.GuiCurrState is STATE_WAIT_DIAGNOSTIC:

                DiagCurrState = self.Diag_State.value

                if DiagCurrState is 0:
                    self.GuiCurrState = STATE_SEND_RESULT

            elif self.GuiCurrState is STATE_SEND_RESULT:

                print("\n> Se recibe resultado de PEATC_Diag")
                DiagnPEATC = self.Diag_Result_output.recv()
                self.GuiUpdateDiag.value = DiagnPEATC[3]

                print(DiagnPEATC[3])
                print(self.__StateVal2key(DiagnPEATC[3], Diag_Dict))
                print("---------")
                self.GuiCurrState = STATE_CREATING_LOG
                print("---------")

            elif self.GuiCurrState is STATE_CREATING_LOG:

                print("---Creating CSV File----")
                now = datetime.now()

                dt_LogNameB = self.__Cmd_LogName[:self.__Cmd_DiagAge[2]].decode(
                    'UTF-8')
                dt_string = str(dt_LogNameB)
                # dt_string = now.strftime("%d-%m-%Y_%H.%M.%S")
                print("Creating CSV File in the following direction")
                LogFilePath = APP_LOGS_PATH + 'Log_' + dt_string + '.csv'
                print(LogFilePath)

                CsvWaveData = []

                for MemIndex in range(len(CONFIG_SignaldB)):
                    CsvWaveData.append(
                        {'SignaldB': self.WaveData[MemIndex]['SignaldB'],
                         'Wave': self.WaveData[MemIndex]['Wave'],
                         'FullSignal': self.WaveData[MemIndex]['FullSignal'],
                         'Diagnostic': self.GuiUpdateDiag.value})

                print("\nWriting following data in the csv file")
                print(CsvWaveData)

                with open(LogFilePath, 'w',
                          encoding='UTF8', newline='') as CurrDiagData:
                    writer = csv.DictWriter(CurrDiagData, fieldnames=[
                        'SignaldB', 'Wave', 'FullSignal', 'Diagnostic'])
                    writer.writeheader()
                    writer.writerows(CsvWaveData)

                self.GuiCurrState = STATE_STAND_BY

            elif self.GuiCurrState is STATE_RESET:

                for i, dic in enumerate(self.WaveData):
                    GetPEATCDict = self.WaveData[i]

                    GetPEATCDict['NewData'] = 0
                    GetPEATCDict['Wave'] = []
                    GetPEATCDict['FullSignal'] = []
                    self.WaveData[i] = GetPEATCDict
                    self.ArrNewData[i] = 0

                self.GuiUpdateDiag.value = Diag_Dict["No Diagnostic"]

                if self.__Cmd_Reset[1] is 0 and self.__Cmd_Reset[3] is 0:
                    if self.__Cmd_Reset[2] is 0:
                        self.__Cmd_Reset[0] = 0
                        print("> Reset Diag")

                self.GuiCurrState = STATE_STAND_BY
            else:
                self.GuiCurrState = self.GuiCurrState
