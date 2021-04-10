import os
import sys
import struct

_TEST_PATH = os.getcwd()
BASE_CB_PATH = _TEST_PATH + "\\.."
#print(BASE_CB_PATH)

sys.path.append(
    BASE_CB_PATH)

import _Test_RawVal_PEATC as Test_Vec
import PEATC_Analyze
import PEATC_Control

TEST_RAW_PATH_TEMP_6 = _TEST_PATH + "\\_TestTempFile_6.tmp"
TEST_RAW_PATH_TEMP_12 = _TEST_PATH + "\\_TestTempFile_12.tmp"
TEST_RAW_PATH_TEMP_20 = _TEST_PATH + "\\_TestTempFile_20.tmp"

#-------------------------Utilidades---------------------------------

def GenRawFile(TEMP_PATH, TEST_VECTOR):

    with open(TEMP_PATH, 'wb') as FileGs_Raw:
        ByteSplit = [0, 0]
        Raw_Data_list = TEST_VECTOR
        for i in range(len(Raw_Data_list)):
            RawStream = Raw_Data_list[i]
            if RawStream <= 0xFF:
                ByteSplit[0] = 0x0
                ByteSplit[1] = RawStream
            elif RawStream <= 0xFFFF:
                ByteSplit[0] = int((0xFF00 & RawStream) / 256)
                ByteSplit[1] = 0xFF & RawStream

            FileGs_Raw.write(struct.pack('B' * 2, ByteSplit[0], ByteSplit[1]))

#-------------------------PRE-TEST---------------------------------


GenRawFile(TEST_RAW_PATH_TEMP_6, Test_Vec.Test_AS_Raw_Data_6_month)
GenRawFile(TEST_RAW_PATH_TEMP_12, Test_Vec.Test_AS_Raw_Data_12_month)
GenRawFile(TEST_RAW_PATH_TEMP_20, Test_Vec.Test_AS_Raw_Data_20_month)

#---------------------------TEST-----------------------------------


print("----------Test_CB_1.1 Start---------")

PEATC_Analyze.AnalyzeSignal("_TestTempFile_6.tmp")

print("----------Test_CB_1.1 End-----------")
print("----------Test_CB_1.2 Start---------")

PEATC_Analyze.AnalyzeSignal("_TestTempFile_12.tmp")

print("----------Test_CB_1.2 End-----------")
print("----------Test_CB_1.3 Start---------")

PEATC_Analyze.AnalyzeSignal("_TestTempFile_20.tmp")

print("----------Test_CB_1.3 End-----------")

print("----------Test_CB_2 Start-----------")

PEATC_Analyze.AnalyzeSignal("_TestTempFile_20.tmp")

print("----------Test_CB_2 End-------------")


#-------------------------POST-TEST---------------------------------
