import os
import sys
import Xillybus

PEATC_DIAGNOSTIC_PATH = os.path.dirname(os.path.realpath(__file__))
CONFIG_DRIVE_PATH = PEATC_DIAGNOSTIC_PATH + "\\..\\Config"
sys.path.append(
    CONFIG_DRIVE_PATH)

from PEATC_Config import*

'''!
Ruta para el arvhivo para reiniciar la logica
en el FPGA
'''
if PEATC_CONFIG_CURR_OS is "Linux":
    if PEATC_CONFIG_TEST_MODE is False:
        RN_FPGA_RESET_PATH = '/dev/xillybus_fpga_reset'
    else:
        RN_FPGA_RESET_PATH = PEATC_DIAGNOSTIC_PATH + "/dev/xillybus_fpga_reset"
else:
    RN_FPGA_RESET_PATH = PEATC_DIAGNOSTIC_PATH + "\\dev\\xillybus_fpga_reset"

'''!
Ruta para el arvhivo que contiene los datos
crudos transmitido del sistema RN al host
'''
if PEATC_CONFIG_CURR_OS is "Linux":
    if PEATC_CONFIG_TEST_MODE is False:
        RN_PARAM_PATH = '/dev/xillybus_rn_diag_param'
    else:
        RN_PARAM_PATH = PEATC_DIAGNOSTIC_PATH + "/dev/xillybus_rn_diag_param"
else:
    RN_PARAM_PATH = PEATC_DIAGNOSTIC_PATH + "\\dev\\xillybus_rn_diag_param"

'''!
Ruta para el arvhivo que contiene los datos
crudos transmitido del sistema RN al host
'''
if PEATC_CONFIG_CURR_OS is "Linux":
    if PEATC_CONFIG_TEST_MODE is False:
        RN_RESULT_PATH = '/dev/xillybus_rn_diag_result'
    else:
        RN_RESULT_PATH = PEATC_DIAGNOSTIC_PATH + "/dev/xillybus_rn_diag_result"       
else:
    RN_RESULT_PATH = PEATC_DIAGNOSTIC_PATH + "\\dev\\xillybus_rn_diag_result"


class PEATC_Diagnostic:
    '''!
    Driver para el sistema donde se implementa la red neuronal.
    '''

    IsSingleton = None

    def __new__(self):
        '''!
        Implementación del patrón de diseño singelton,
        ya que se debe resguardar la manipulación de los
        archivos del Xillybus, ya que el manipular dichos
        archivos influye en señales de Hw generadas por el
        core del Xillybus
        '''
        if self.IsSingleton is None:
            self.IsSingleton = super(PEATC_Diagnostic, self).__new__(self)
        return self.IsSingleton

    def SetMatrix(self, PatientAge: int, MatrixParams: list):
        '''!
        Establece en formato la matriz con los resultados
        de la prueba de PEATC para ser enviados como
        perametros de entrada a la red neuronal.

        @param MatrixParams  Matriz con los parametro de entrada
        los cuales constan de Amp TxWx | Lat TxWx:
        |Amp T1W1|Lat T1W1|Amp T1W(..)|Lat T1W(..)|Amp T1Wn|Lat T1Wn
        |Amp T(..)W1|Lat T(..)W1|Amp T(..)W(..)|Lat T(..)W(..)|Amp T(..)W(n)
        |Lat T(..)W(n)|Amp TmW1|Lat TmW1|Amp TmW(..)| Lat TmW(..)|Amp TmW(n)
        |Lat TmW(n)
        (donde m = numero de pruebas, n = 5, Amp = Amplitud,
        Lat = latencia, Tx = Test x, Wx = Wave x)
        '''

        '''
        Asignación de trama para el comando enviado al sistema RN
        '''
        Xillybus.memory_write(RN_FPGA_RESET_PATH, [0,0,0,0])

        MatrixStream = [PatientAge]
        MatrixStream.extend(MatrixParams)
        ByteSplit = [0, 0]
        ByteStream = []

        for IndexMatrix in range(len(MatrixStream)):

            if MatrixStream[IndexMatrix] <= 0xFF:
                ByteSplit[0] = 0x0
                ByteSplit[1] = MatrixStream[IndexMatrix]
            elif MatrixStream[IndexMatrix] <= 0xFFFF:
                ByteSplit[0] = int((0xFF00 & MatrixStream[IndexMatrix]) / 256)
                ByteSplit[1] = 0xFF & MatrixStream[IndexMatrix]

            ByteStream.extend(ByteSplit)

        Xillybus.memory_write(RN_PARAM_PATH, ByteStream)

    def GetDiagnostic(self) -> int:
        '''!
        Lee el archivo de Xillybus donde se encientra el diagnostico retornado
        por la red neuronal.

        @return Codigo de diagnostico
        '''
        ReadDiagData = Xillybus.memory_read(RN_RESULT_PATH, 4)

        print(ReadDiagData)
        return ReadDiagData
