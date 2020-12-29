import Xillybus
import struct

'''!
Ruta para el arvhivo que transmite del host
al sistema GS_AS
'''
# GS_START_PATH = '/dev/xillybus_gs_start_test'
GS_START_PATH = 'E:\\ARCHIVOS_Y_DOCUMENTOS\\01_Tesis_Local\\PEATC_App\\Low_Drivers\\dev\\xillybus_gs_start_test'
# GS_START_PATH = 'dev\\xillybus_gs_start_test'


'''!
Ruta para el arvhivo que contiene los datos
crudos transmitido del sistema GS_AS al host
'''
# GS_RAW_PATH = '/dev/xillybus_gs_raw_signal'
GS_RAW_PATH = 'E:\\ARCHIVOS_Y_DOCUMENTOS\\01_Tesis_Local\\PEATC_App\\Low_Drivers\\dev\\xillybus_gs_raw_signal'
# GS_RAW_PATH = 'dev\\xillybus_gs_raw_signal'


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

        for key in TestParamsLimits:

            if int(TestProfile[key]) < 0 and int(TestProfile[key]) > TestParamsLimits[key]:

                print(str(key) + " Out of limit:" +
                      " current limit value ".join(str(TestParamsLimits[key])))
                exit(1)

        '''
        Asignación de trama para el comando enviado al sistema GS_AS
        '''
        TestParams = (int(TestProfile["Gs_Latency"]),
                      int(TestProfile["Gs_SignaldB"]),
                      int(TestProfile["Gs_Polarity"]),
                      int(TestProfile["Gs_Freq"]))

        Xillybus.memory_write(GS_START_PATH, TestParams)

    def GetRawSignal(self, Temp_file: str):
        '''!
        Crea un archivo con la señal cruda resultante de
        la lectura analogica de PEATC

        @param Temp_file  Ruta del archivo temporal donde
        se almacenara la señal cruda de PEATC
        '''
        with open(Temp_file, 'w') as TempFile:
            # convertir y justificar constante
            ReadGenData = Xillybus.stream_read(GS_RAW_PATH)
            ReadData = next(ReadGenData)
            Index = 0
            Byte2Word = 0
            while Index < (len(ReadData) - 1):
                Byte2Word = (ReadData[Index] * 256) + ReadData[Index + 1]
                Index += 2
                TempFile.write(str(Byte2Word) + " ")
