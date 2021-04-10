import os
import sys

CURR_PATH = os.path.dirname(os.path.realpath(__file__))
LOW_DRIVE_PATH = CURR_PATH + "\\..\\Low_Drivers"

print(CURR_PATH)

sys.path.append(
    LOW_DRIVE_PATH)

import PEATC_Analyze
import PEATC_Diagnostic
import PEATC_GS_AS

'''!
Estado Stand by
'''
STATE_STAND_BY = 0
STATE_RESET = 1
STATE_ = 1


class PEATC_Control:
    '''!
    Controlador de la aplicación para obtener los datos
    crudos de las señales de PEATC, analizarlas y reportar los
    resultados de los análisis

    @note Este módulo comunica y controla los módulos
    de la capa Low Drive, además de exponer en su interfaz la
    información a la tarea donde se ejecuta la interfaz grafica
    '''

    PeatcCurrState = 

    def __init__(self):
        '''!
        Inicializa la maquina de estados para realizar la pruena de PEATC
        '''
