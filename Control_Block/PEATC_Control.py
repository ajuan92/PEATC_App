import os
import sys
from time import time

CURR_PATH = os.path.dirname(os.path.realpath(__file__))
LOW_DRIVE_PATH = CURR_PATH + "\\..\\Low_Drivers"
TEMP_RAW_DATA = LOW_DRIVE_PATH + "\\TempRawData.tmp"

sys.path.append(
    LOW_DRIVE_PATH)

from PEATC_Analyze import AnalyzeSignal
from PEATC_GS_AS import PEATC_Gs_As
from PEATC_Diagnostic import PEATC_Diagnostic

PEATC_CONFIG_SAMPLE_WAIT_TIME = 1  # 10
PEATC_CONFIG_DIAG_WAIT_TIME = 1  # 10
'''!
Comandos
'''
PEATC_CONTROL_CMD_START_TEST = 1
PEATC_CONTROL_CMD_STOP_TEST = 0

PEATC_Ctrl_Cmd_Dict = {
    "Cmd": 0,
    "Gs_SignaldB": 0,
    "Gs_Latency": 0,
    "Gs_Polarity": 0,
    "Gs_Freq": 0,
}

'''!
Estado Stand by
'''
PEATC_CONTROL_STATE_STAND_BY = 0
PEATC_CONTROL_STATE_RESET = 1
PEATC_CONTROL_STATE_INIT_TEST = 2
PEATC_CONTROL_STATE_WAIT_RAW_DATA = 3
PEATC_CONTROL_STATE_ANALYZE_DATA = 4
PEATC_CONTROL_STATE_INIT_DIAGNOSTIC = 5
PEATC_CONTROL_STATE_WAIT_DIAGNOSTIC = 6
PEATC_CONTROL_STATE_SEND_RESULT = 7

PEATC_Ctrl_State_Dict = {
    PEATC_CONTROL_STATE_STAND_BY: "PEATC_CONTROL_STATE_STAND_BY",
    PEATC_CONTROL_STATE_RESET: "PEATC_CONTROL_STATE_RESET",
    PEATC_CONTROL_STATE_INIT_TEST: "PEATC_CONTROL_STATE_INIT_TEST",
    PEATC_CONTROL_STATE_WAIT_RAW_DATA: "PEATC_CONTROL_STATE_WAIT_RAW_DATA",
    PEATC_CONTROL_STATE_ANALYZE_DATA: "PEATC_CONTROL_STATE_ANALYZE_DATA",
    PEATC_CONTROL_STATE_INIT_DIAGNOSTIC: "PEATC_CONTROL_STATE_INIT_DIAGNOSTIC",
    PEATC_CONTROL_STATE_WAIT_DIAGNOSTIC: "PEATC_CONTROL_STATE_WAIT_DIAGNOSTIC",
    PEATC_CONTROL_STATE_SEND_RESULT: "PEATC_CONTROL_STATE_SEND_RESULT"
}


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
        print("Inicializacion del modulo PEATC_Control")
        print(CURR_PATH)
        sys.stdout.flush()

    def __ReportState(self, Arg_State, CurrState):
        '''!
        Reporta códigos de estado del driver que captura la señal de PEATC
        '''

        if Arg_State.empty() is True:
            if Arg_State.full() is True:
                Arg_State.get(block=True, timeout=1)

        else:
            if Arg_State.full() is False:
                Arg_State.get(block=True, timeout=1)
            Arg_State.put(CurrState, block=True, timeout=1)

    def ControlHandler(self, Arg_Cmd, Arg_Results, Arg_State):
        '''!
        Maneja la maquina de estados para la realización de la
        prueba de PEATC, así como la captura de la señal de PEATC.

        @param Arg_Cmd Conducto para recibir comandos que inician
        la prueba de PEATC

        @param Arg_Results Conducto para enviar los datos capturados
        de la señal de PEATC obtenida

        @param Arg_State Conducto para enviar el código de estado
        del driver que captura la señal de PEATC
        '''
        print("> Inicio Modulo PEATC_Control Tarea ControlHandler")
        sys.stdout.flush()

        Control_GS_AS = PEATC_Gs_As()

        TimeStamp = 0
        PeatcCurrState = PEATC_CONTROL_STATE_STAND_BY
        CurrCmd = PEATC_Ctrl_Cmd_Dict
        PeatcWaves = []
        FullWaveData = []

        while True:

            if Arg_State is not PeatcCurrState:
                Arg_State = PeatcCurrState

            if PeatcCurrState is PEATC_CONTROL_STATE_STAND_BY:

                CurrCmd = Arg_Cmd.recv()
                print("\n===" + os.path.basename(CURR_PATH) + "===")
                print("Se recibe Cmd en PEATC_Ctrl")
                print(CurrCmd)
                print("====================\n")
                sys.stdout.flush()

                if CurrCmd["Cmd"] is PEATC_CONTROL_CMD_START_TEST:
                    PeatcCurrState = PEATC_CONTROL_STATE_INIT_TEST

            elif PeatcCurrState is PEATC_CONTROL_STATE_INIT_TEST:

                CurrParams = {
                    "Gs_SignaldB": CurrCmd["Gs_SignaldB"],
                    "Gs_Latency": CurrCmd["Gs_Latency"],
                    "Gs_Polarity": CurrCmd["Gs_Polarity"],
                    "Gs_Freq": CurrCmd["Gs_Freq"],
                }

                Control_GS_AS.InitTest(**CurrParams)

                TimeStamp = time()
                PeatcCurrState = PEATC_CONTROL_STATE_WAIT_RAW_DATA

            elif PeatcCurrState is PEATC_CONTROL_STATE_WAIT_RAW_DATA:

                if (time() - TimeStamp) > PEATC_CONFIG_SAMPLE_WAIT_TIME:
                    PeatcCurrState = PEATC_CONTROL_STATE_ANALYZE_DATA

            elif PeatcCurrState is PEATC_CONTROL_STATE_ANALYZE_DATA:

                Control_GS_AS.GetRawSignal(TEMP_RAW_DATA)
                PeatcWaves, FullWaveData = AnalyzeSignal(TEMP_RAW_DATA)

                PeatcCurrState = PEATC_CONTROL_STATE_SEND_RESULT

            elif PeatcCurrState is PEATC_CONTROL_STATE_SEND_RESULT:

                Arg_Results.send((PeatcWaves, FullWaveData))
                PeatcCurrState = PEATC_CONTROL_STATE_RESET

            elif PeatcCurrState is PEATC_CONTROL_STATE_RESET:

                PeatcCurrState = PEATC_CONTROL_STATE_STAND_BY
                TimeStamp = 0
                CurrCmd = PEATC_Ctrl_Cmd_Dict
                PeatcWaves.clear()
                FullWaveData = []

    def DiagHandler(self, Arg_PeatcTable, Arg_DiagResults, Arg_State):
        '''!
        Maneja la maquina de estados para la realización del diagnostico
        de las señales de PEATC.

        @param Arg_PeatcTable Conducto para recibir la tabla de
        propiedades de las señales de PEATC

        @param Arg_DiagResults Conducto para enviar el resultado
        del diagnostico de las señales de PEATC

        @param Arg_State Conducto para enviar el código de estado
        del driver para el diagnostico de las señal de PEATC
        '''
        print("> Inicio Modulo PEATC_Control Tarea DiagHandler")
        sys.stdout.flush()

        Diag_Sys = PEATC_Diagnostic()

        TimeStamp = 0
        DiagCurrState = PEATC_CONTROL_STATE_STAND_BY
        CurrTable = None

        while True:

            if Arg_State is not DiagCurrState:
                Arg_State = DiagCurrState

            if DiagCurrState is PEATC_CONTROL_STATE_STAND_BY:

                CurrTable = Arg_PeatcTable.recv()

                if CurrTable is not None:
                    DiagCurrState = PEATC_CONTROL_STATE_INIT_DIAGNOSTIC
                    print("===" + os.path.basename(CURR_PATH) + "===")
                    print("Se recibe Cmd en PEATC_Diag")
                    print("Wave Amp & Lat")
                    print(CurrTable)
                    print("====================\n")
                    sys.stdout.flush()

            elif DiagCurrState is PEATC_CONTROL_STATE_INIT_DIAGNOSTIC:

                MatrixParam = []

                for IndexTable in range(len(CurrTable[1])):

                    for IndexWaves in range(len(CurrTable[1][IndexTable])):

                        if len(CurrTable[1][IndexTable][IndexWaves]) is not 0:
                            MatrixParam.extend(
                                CurrTable[1][IndexTable][IndexWaves])
                        else:
                            MatrixParam.extend([0, 0])

                Diag_Sys.SetMatrix(CurrTable[0], MatrixParam)

                TimeStamp = time()
                DiagCurrState = PEATC_CONTROL_STATE_WAIT_DIAGNOSTIC

            elif DiagCurrState is PEATC_CONTROL_STATE_WAIT_DIAGNOSTIC:

                if (time() - TimeStamp) > PEATC_CONFIG_DIAG_WAIT_TIME:
                    DiagCurrState = PEATC_CONTROL_STATE_SEND_RESULT

            elif DiagCurrState is PEATC_CONTROL_STATE_SEND_RESULT:

                CurrDiagnostic = Diag_Sys.GetDiagnostic()
                Arg_DiagResults.send(CurrDiagnostic)

                DiagCurrState = PEATC_CONTROL_STATE_RESET

            elif DiagCurrState is PEATC_CONTROL_STATE_RESET:
                TimeStamp = 0
                DiagCurrState = PEATC_CONTROL_STATE_STAND_BY
                CurrTable = None
