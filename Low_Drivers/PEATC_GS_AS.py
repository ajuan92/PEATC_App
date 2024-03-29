import os
import sys
import Xillybus
import struct

PEATC_GS_AS_PATH = os.path.dirname(os.path.realpath(__file__))

try:
    CONFIG_DRIVE_PATH = PEATC_GS_AS_PATH + "\\..\\Config"
    sys.path.append(
        CONFIG_DRIVE_PATH)
except ImportError:
    print(CONFIG_DRIVE_PATH)
else:
    CONFIG_DRIVE_PATH = PEATC_GS_AS_PATH + "/../Config"
    sys.path.append(
        CONFIG_DRIVE_PATH)

from PEATC_Config import*

'''!
Ruta para el arvhivo para reiniciar la logica
en el FPGA
'''
if PEATC_CONFIG_CURR_OS is "Linux":
    if PEATC_CONFIG_TEST_MODE is False:
        GS_FPGA_RESET_PATH = '/dev/xillybus_fpga_reset'
    else:
        GS_FPGA_RESET_PATH = PEATC_GS_AS_PATH + "/dev/xillybus_fpga_reset"
else:
    GS_FPGA_RESET_PATH = PEATC_GS_AS_PATH + "\\dev\\xillybus_fpga_reset"

'''!
Ruta para el arvhivo que transmite del host
al sistema GS_AS
'''
if PEATC_CONFIG_CURR_OS is "Linux":
    if PEATC_CONFIG_TEST_MODE is False:
        GS_START_PATH = '/dev/xillybus_gs_start_test'
    else:
        GS_START_PATH = PEATC_GS_AS_PATH + "/dev/xillybus_gs_start_test"
else:
    GS_START_PATH = PEATC_GS_AS_PATH + "\\dev\\xillybus_gs_start_test"


'''!
Ruta para el arvhivo que contiene los datos
crudos transmitido del sistema GS_AS al host
'''
if PEATC_CONFIG_CURR_OS is "Linux":
    if PEATC_CONFIG_TEST_MODE is False:
        GS_RAW_PATH = '/dev/xillybus_gs_raw_signal'
    else:
        GS_RAW_PATH = PEATC_GS_AS_PATH + "/dev/xillybus_gs_raw_signal"
else:
    GS_RAW_PATH = PEATC_GS_AS_PATH + "\\dev\\xillybus_gs_raw_signal"


TestParamsLimits = {
    'Gs_SignaldB': 70,
    'Gs_Latency': 100,
    'Gs_Polarity': 1,
    'Gs_Freq': 60,
}


class PEATC_Gs_As:
    '''!
    Driver para el sistema Generate Signal, Analog Signal
    '''

    IsSingleton = None

    def __new__(self):
        '''!
        Implementación del patrón de diseño singelton,
        ya que se debe resguardar la manipulación de los
        archivos del Xillybus, ya que el manipular dichos
        archivos influye en señales de Hw generadas por el
        core del Xillibus
        '''
        if self.IsSingleton is None:
            self.IsSingleton = super(PEATC_Gs_As, self).__new__(self)
        return self.IsSingleton

    def InitTest(self, **TestProfile):
        '''!
        Driver para el sistema Generate Signal, Analog Signal

        @param TestProfile  Trama de la configuración para
        generar el estimulo sonoro en el sistema GS
        '''

        '''
        Revisión de valores limite en parametros para la
        generación de la señal estimulo
        '''
        Xillybus.memory_write(GS_FPGA_RESET_PATH, [0, 0, 0, 0])

        for key in TestParamsLimits:

            if int(TestProfile[key]) < 0 and int(TestProfile[key]) > TestParamsLimits[key]:

                print(str(key) + " Out of limit:" +
                      " current limit value ".join(str(TestParamsLimits[key])))
                exit(1)

        '''
        Asignación de trama para el comando enviado al sistema GS_AS
        '''
        TestParams = (int(TestProfile["Gs_Latency"]),
                      int(TestProfile["Gs_Polarity"]),
                      int(TestProfile["Gs_Freq"]),
		      int(TestProfile["Gs_SignaldB"]))

        print("===" + "PEATC_GS_AS" + "===")
        print("Cmd")
        print(TestParams)
        Xillybus.memory_write(GS_START_PATH, TestParams)

    def GetRawSignal(self, Temp_file: str):
        '''!
        Crea un archivo con la señal cruda resultante de
        la lectura analogica de PEATC

        @param Temp_file  Ruta del archivo temporal donde
        se almacenara la señal cruda de PEATC
        '''
        with open(Temp_file, 'wb') as TempFile:
            # convertir y justificar constante
            ReadGenData = Xillybus.stream_read(dev_file=GS_RAW_PATH,
                                               length=PEATC_CONFIG_EXPECTED_SIGNAL_SAMPLES)
            ReadData = next(ReadGenData)
            print("===" + "PEATC_GS_AS" + "===")
            print("Raw signal")
            print(ReadData)
            print("====================\n")
            sys.stdout.flush()

            TempFile.write(struct.pack('B' * len(ReadData), *ReadData))
