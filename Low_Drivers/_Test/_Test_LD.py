import os
import sys

_TEST_PATH = os.getcwd()
BASE_LD_PATH = _TEST_PATH + "\\.."

sys.path.append(
    BASE_LD_PATH)

print(BASE_LD_PATH)

from PEATC_GS_AS import PEATC_Gs_As
from PEATC_Diagnostic import PEATC_Diagnostic
from _Test_RawVal_PEATC import*
import struct

TEST_GS_START_PATH = BASE_LD_PATH + "\\dev\\xillybus_gs_start_test"
TEST_GS_RAW_PATH = BASE_LD_PATH + "\\dev\\xillybus_gs_raw_signal"

TEST_RN_DIAG_PARAM = BASE_LD_PATH + "\\dev\\xillybus_rn_diag_param"
TEST_RN_DIAG_RESULT = BASE_LD_PATH + "\\dev\\xillybus_rn_diag_result"


# -------------------------PRE-TEST---------------------------------

with open(TEST_GS_START_PATH, 'w') as FileGs_Start:
    pass

with open(TEST_GS_RAW_PATH, 'wb') as FileGs_Raw:
    ByteSplit = [0, 0]
    Raw_Data_list = Test_AS_Raw_Data_20_month
    for i in range(len(Raw_Data_list)):
        RawStream = Raw_Data_list[i]
        if RawStream <= 0xFF:
            ByteSplit[0] = 0x0
            ByteSplit[1] = RawStream
        elif RawStream <= 0xFFFF:
            ByteSplit[0] = int((0xFF00 & RawStream) / 256)
            ByteSplit[1] = 0xFF & RawStream

        FileGs_Raw.write(struct.pack('B' * 2, ByteSplit[0], ByteSplit[1]))

with open(TEST_RN_DIAG_PARAM, 'wb') as FileDiag_Param:
    pass

with open(TEST_RN_DIAG_RESULT, 'wb') as FileDiag_Raw:
    FileDiag_Raw.write(struct.pack('b' * 4, 0, 0, 0, 0x5))
    pass


# -------------------------TEST---------------------------------
print("----------Test_LD_1 Start---------")

Sys_GS_AS = PEATC_Gs_As()
Singelton_GS_AS = PEATC_Gs_As()

print(Sys_GS_AS is Singelton_GS_AS)

Sys_Diagnostic = PEATC_Diagnostic()
Singelton_Diagnostic = PEATC_Diagnostic()

print(Sys_Diagnostic is Singelton_Diagnostic)

print("----------Test_LD_1 End-----------")
print("----------Test_LD_2 Start---------")

TestPerfil = {'Gs_Latency': 100, 'Gs_SignaldB': 70,
              'Gs_Polarity': 1, 'Gs_Freq': 60}

Sys_GS_AS.InitTest(**TestPerfil)

with open(TEST_GS_START_PATH, 'rb') as FileGs_Start:
    data = FileGs_Start.read(4)
    print(data)
    data1 = struct.unpack('B' * 4, data)
    print(data1[0])
    print(data1[1])
    print(data1[2])
    print(data1[3])

print("----------Test_LD_2 End-----------")
print("----------Test_LD_3 Start---------")

PATH_TestTempFile = '_TestTempFile.tmp'

Sys_GS_AS.GetRawSignal(PATH_TestTempFile)

with open(PATH_TestTempFile, 'r') as FileGs_Raw:
    print(FileGs_Raw.read())
    pass

with open(PATH_TestTempFile, 'r') as FileGs_Raw:
    pass

print("----------Test_LD_3 End-----------")
print("----------Test_LD_4 Start---------")

AgeInMonth = 12
SinteticMatix = [42, 1500, 35, 2800, 43, 3800, 41, 5500, 46, 6000]

Sys_Diagnostic.SetMatrix(AgeInMonth, SinteticMatix)

with open(TEST_RN_DIAG_PARAM, 'rb') as FileDiag_Param:
    print(FileDiag_Param.read())
    pass

print("----------Test_LD_4 End-----------")
print("----------Test_LD_5 Start---------")

AgeInMonth = 12
SinteticMatix = [42, 1500, 35, 2800, 43, 3800, 41, 5500, 46, 6000]
TeenSamples = []

for TestIndex in range(10):
    TeenSamples.extend(SinteticMatix)

Sys_Diagnostic.SetMatrix(AgeInMonth, TeenSamples)

with open(TEST_RN_DIAG_PARAM, 'rb') as FileDiag_Param:
    print(FileDiag_Param.read())
    pass

print("----------Test_LD_5 End-----------")
print("----------Test_LD_6 Start---------")

DiagCode = Sys_Diagnostic.GetDiagnostic()
print(DiagCode)

print("----------Test_LD_6 End-----------")

# -------------------------POST-TEST--------------------------------
with open(TEST_GS_START_PATH, 'r') as FileGs_Start:
    pass

with open(TEST_GS_RAW_PATH, 'r') as FileGs_Raw:
    pass

with open(TEST_RN_DIAG_PARAM, 'r') as FileDiag_Param:
    pass

with open(TEST_RN_DIAG_RESULT, 'r') as FileDiag_Param:
    pass
