import Xillybus

'''!
Ruta para el arvhivo que contiene los datos
crudos transmitido del sistema RN al host
'''
#RN_PARAM_PATH = '/dev/xillybus_rn_diag_param'
RN_PARAM_PATH = 'E:\\ARCHIVOS_Y_DOCUMENTOS\\01_Tesis_Local\\PEATC_App\\Low_Drivers\\dev\\xillybus_rn_diag_param'
#RN_PARAM_PATH = 'dev\\xillybus_rn_diag_param'

'''!
Ruta para el arvhivo que contiene los datos
crudos transmitido del sistema RN al host
'''
#RN_RESULT_PATH = '/dev/xillybus_rn_diag_result'
RN_RESULT_PATH = 'E:\\ARCHIVOS_Y_DOCUMENTOS\\01_Tesis_Local\\PEATC_App\\Low_Drivers\\dev\\xillybus_rn_diag_result'
#RN_RESULT_PATH = 'dev\\xillybus_rn_diag_result'


class PEATC_Diagnostic:
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
            self.IsSingleton = super(PEATC_Diagnostic, self).__new__(self)
        return self.IsSingleton

    def SetMatrix(self, *MatrixParams, PatientAge):
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

        MatrixStream = [PatientAge]
        for TestIndex in range(len(MatrixParams)):
            MatrixStream.Extend(MatrixParams[TestIndex])

        Xillybus.stream_write(RN_PARAM_PATH, MatrixStream)

    def GetDiagnostic(self, Temp_file: str):
        '''!
        Crea un archivo con la señal cruda resultante de
        la lectura analogica de PEATC

        @param Temp_file  Ruta del archivo temporal donde
        se almacenara la señal cruda de PEATC
        '''
        with open(Temp_file, 'w') as TempFile:
            # convertir y justificar constante
            ReadCheck = Xillybus.stream_read(GS_RAW_PATH, 100)
            ReadGenData = next(ReadCheck)
            print(ReadGenData)
            for ReadGenData in ReadCheck:
                TempFile.write(''.join(ReadGenData))
