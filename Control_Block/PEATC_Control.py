import os
import sys
from time import time
from multiprocessing import Process, Pipe

CURR_PATH = os.path.dirname(os.path.realpath(__file__))
LOW_DRIVE_PATH = CURR_PATH + "\\..\\Low_Drivers"

sys.path.append(
    LOW_DRIVE_PATH)

from PEATC_Analyze import AnalyzeSignal
from PEATC_GS_AS import PEATC_Gs_As
from PEATC_Diagnostic import PEATC_Diagnostic

PEATC_CONFIG_SAMPLE_WAIT_TIME = 2
PEATC_CONFIG_DIAG_WAIT_TIME = 2
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


class PEATC_Control(PEATC_Gs_As, PEATC_Diagnostic):
    '''!
    Controlador de la aplicación para obtener los datos
    crudos de las señales de PEATC, analizarlas y reportar los
    resultados de los análisis

    @note Este módulo comunica y controla los módulos
    de la capa Low Drive, además de exponer en su interfaz la
    información a la tarea donde se ejecuta la interfaz grafica
    '''

    def __init__(self):
        '''!
        Inicializa la maquina de estados para realizar la prueba de PEATC
        '''
        print("Inicialización del modulo PEATC_Control")

    def ControlHandler(self, Arg_Cmd, Arg_Results, Arg_State):
        '''!
        Parte central de la tarea de control, maneja la maquina
        de estados para la realización de la prueba de PEATC, así
        como manjear los mecanismos de comunicación de entrada y
        salida.

        @param Arg_Cmd Conducto para recibir comandos que disparan
        las transiciones de la maquina de estado

        @param Arg_Results Conducto para enviar los resultados
        de la prueba de PEATC

        @param Arg_State Conducto para enviar códigos de Estado
        '''
        print("Inicio Tarea de Control")
        sys.stdout.flush()

        Control_GS_AS = PEATC_Gs_As()

        TimeStamp = 0
        PeatcCurrState = STATE_STAND_BY
        CurrCmd = Cmd_Template
        PeatcWaves = []
        FullWaveData = []

        while True:

            if PeatcCurrState is STATE_STAND_BY:

                CurrCmd = Arg_Cmd.recv()

                if CurrCmd["Cmd"] is PEATC_CONFIG_CMD_START_TEST:
                    PeatcCurrState = STATE_INIT_TEST

            elif PeatcCurrState is STATE_INIT_TEST:

                CurrParams = {
                    "Gs_SignaldB": CurrCmd["Gs_SignaldB"],
                    "Gs_Latency": CurrCmd["Gs_Latency"],
                    "Gs_Polarity": CurrCmd["Gs_Polarity"],
                    "Gs_Freq": CurrCmd["Gs_Freq"],
                }

                print(CurrParams)  # QUITAR TEST
                sys.stdout.flush()

                Control_GS_AS.InitTest(**CurrParams)

                TimeStamp = time()
                PeatcCurrState = STATE_WAIT_RAW_DATA

            elif PeatcCurrState is STATE_WAIT_RAW_DATA:

                if (time() - TimeStamp) > PEATC_CONFIG_SAMPLE_WAIT_TIME:
                    PeatcCurrState = STATE_ANALYZE_DATA

            elif PeatcCurrState is STATE_ANALYZE_DATA:

                Control_GS_AS.GetRawSignal("TempRawData.tmp")

                with open("TempRawData.tmp", 'rb') as FileDiag_Param:
                    print(FileDiag_Param.read())
                    sys.stdout.flush()

                PeatcWaves, FullWaveData = AnalyzeSignal("TempRawData.tmp")

                PeatcCurrState = STATE_SEND_RESULT

            elif PeatcCurrState is STATE_SEND_RESULT:

                Arg_Results.send((PeatcWaves, FullWaveData))
                PeatcCurrState = STATE_RESET

            elif PeatcCurrState is STATE_RESET:

                PeatcCurrState = STATE_STAND_BY
                TimeStamp = 0
                CurrCmd = Cmd_Template
                PeatcWaves.clear()
                FullWaveData = []
            Arg_State.send(PeatcCurrState)

    def DiagHandler(self, Arg_PeatcTable, Arg_DiagResults, Arg_State):
        '''!
        Parte central de la tarea de control, maneja la maquina
        de estados para la realización del diagnostico de las
        señales de PEATC, así como manjear los mecanismos de
        comunicación de entrada y salida.

        @param Arg_Cmd Conducto para recibir comandos que disparan
        las transiciones de la maquina de estado

        @param Arg_Results Conducto para enviar los resultados
        de la prueba de PEATC

        @param Arg_State Conducto para enviar códigos de Estado
        '''
        print("Inicio Tarea de Diagnostico")
        sys.stdout.flush()

        Diag_GS_AS = PEATC_Diagnostic()

        TimeStamp = 0
        DiagCurrState = STATE_STAND_BY
        CurrTable = None

        while True:

            if DiagCurrState is STATE_STAND_BY:

                CurrTable = Arg_PeatcTable.recv()

                if CurrTable is not None:
                    DiagCurrState = STATE_INIT_TEST

            elif DiagCurrState is STATE_INIT_DIAGNOSTIC:

                Diag_GS_AS.SetMatrix(,CurrTable)

                TimeStamp = time()
                DiagCurrState = STATE_WAIT_DIAGNOSTIC

            elif DiagCurrState is STATE_WAIT_DIAGNOSTIC:

                if (time() - TimeStamp) > PEATC_CONFIG_DIAG_WAIT_TIME:
                    DiagCurrState = STATE_ANALYZE_DATA

            elif DiagCurrState is STATE_SEND_RESULT:
                pass
            elif DiagCurrState is STATE_SEND_RESULT:
                pass
            elif DiagCurrState is STATE_RESET:
                pass

            Arg_State.send(DiagCurrState)