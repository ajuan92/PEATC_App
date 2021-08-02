import os
import sys
import struct

from GUI_Control import GUI_Control

BASE_PEATC_APP_PATH = os.getcwd()

TEST_LOW_DRIVE = BASE_PEATC_APP_PATH + \
    "\\Low_Drivers\\_Test"

sys.path.append(
    BASE_PEATC_APP_PATH + "\\_Test")

import _Test_RawVal_PEATC as Test_Vec
import PEATC_Analyze as Analyze
import PEATC_Control as Ctrl

TEST_RAW_PATH_TEMP_6 = BASE_PEATC_APP_PATH + "\\_Test\\_TestTempFile_6.tmp"
TEST_RAW_PATH_TEMP_12 = BASE_PEATC_APP_PATH + "\\_Test\\_TestTempFile_12.tmp"
TEST_RAW_PATH_TEMP_20 = BASE_PEATC_APP_PATH + "\\_Test\\_TestTempFile_20.tmp"


TEST_GS_RAW_PATH = BASE_PEATC_APP_PATH + \
    "\\..\\Low_Drivers\\dev\\xillybus_gs_raw_signal"


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

if __name__ == '__main__':

    GenRawFile(TEST_RAW_PATH_TEMP_6, Test_Vec.Test_AS_Raw_Data_6_month)
    GenRawFile(TEST_RAW_PATH_TEMP_12, Test_Vec.Test_AS_Raw_Data_12_month)
    GenRawFile(TEST_RAW_PATH_TEMP_20, Test_Vec.Test_AS_Raw_Data_20_month)

    with open(TEST_GS_RAW_PATH, 'wb') as FileGs_Raw:
        ByteSplit = [0, 0]
        Raw_Data_list = Test_Vec.Test_AS_Raw_Data_20_month
        for i in range(len(Raw_Data_list)):
            RawStream = Raw_Data_list[i]
            if RawStream <= 0xFF:
                ByteSplit[0] = 0x0
                ByteSplit[1] = RawStream
            elif RawStream <= 0xFFFF:
                ByteSplit[0] = int((0xFF00 & RawStream) / 256)
                ByteSplit[1] = 0xFF & RawStream

            FileGs_Raw.write(struct.pack('B' * 2, ByteSplit[0], ByteSplit[1]))

    GUI_Control()
