import sys
sys.path.append(
    "E:\\ARCHIVOS_Y_DOCUMENTOS\\01_Tesis_Local\\PEATC_App\\Low_Drivers")
from PEATC_GS_AS import PEATC_Gs_As
from _Test_RawVal_PEATC import*
import struct

TEST_GS_START_PATH = 'E:\\ARCHIVOS_Y_DOCUMENTOS\\01_Tesis_Local\\PEATC_App\\Low_Drivers\\dev\\xillybus_gs_start_test'
TEST_GS_RAW_PATH = 'E:\\ARCHIVOS_Y_DOCUMENTOS\\01_Tesis_Local\\PEATC_App\\Low_Drivers\\dev\\xillybus_gs_raw_signal'

TEST_RN_DIAG_PARAM = 'E:\\ARCHIVOS_Y_DOCUMENTOS\\01_Tesis_Local\\PEATC_App\\Low_Drivers\\dev\\xillybus_rn_diag_param'
TEST_RN_DIAG_RESULT = 'E:\\ARCHIVOS_Y_DOCUMENTOS\\01_Tesis_Local\\PEATC_App\\Low_Drivers\\dev\\xillybus_rn_diag_result'


#-------------------------PRE-TEST---------------------------------

with open(TEST_GS_START_PATH, 'w') as FileGs_Start:
    pass

with open(TEST_GS_RAW_PATH, 'wb') as FileGs_Raw:
    for i in range(len(Test_AS_Raw_Data_6_month)):
        FileGs_Raw.write(struct.pack('b', Test_AS_Raw_Data_6_month[i]))

with open(TEST_RN_DIAG_PARAM, 'w') as FileGs_Start:
    pass

with open(TEST_RN_DIAG_RESULT, 'wb') as FileGs_Raw:
    pass


#-------------------------TEST---------------------------------

print("----------Test Start 1---------")

PATH_TestTempFile = '_TestTempFile.tmp'

TestPerfil = {'Gs_Latency': 100, 'Gs_SignaldB': 70,
              'Gs_Polarity': 1, 'Gs_Freq': 60}


Sys_GS_AS = PEATC_Gs_As()

Sys_GS_AS.InitTest(**TestPerfil)

with open(TEST_GS_START_PATH, 'rb') as FileGs_Start:
    data = FileGs_Start.read(4)
    print(data)
    data1 = struct.unpack('B' * 4, data)
    print(data1[0])
    print(data1[1])
    print(data1[2])
    print(data1[3])

Sys_GS_AS.GetRawSignal(PATH_TestTempFile)

print("----------Test End 1---------")

#-------------------------POST-TEST--------------------------------
with open(TEST_GS_START_PATH, 'w') as FileGs_Start:
    pass

with open(TEST_GS_RAW_PATH, 'rb') as FileGs_Raw:
    print(FileGs_Raw.read())
    pass
