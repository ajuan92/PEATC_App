import os
import sys
import struct

BASE_PEATC_APP_PATH = os.getcwd()

try:
    CONFIG_DRIVE_PATH = BASE_PEATC_APP_PATH + "\\..\\Config"
    sys.path.append(
        CONFIG_DRIVE_PATH)
except ImportError:
    print(CONFIG_DRIVE_PATH)
else:
    CONFIG_DRIVE_PATH = BASE_PEATC_APP_PATH + "/../Config"
    sys.path.append(
        CONFIG_DRIVE_PATH)
print(CONFIG_DRIVE_PATH)
from PEATC_Config import*

if PEATC_CONFIG_CURR_OS == "Linux":
    TEST_LOW_DRIVE = BASE_PEATC_APP_PATH + \
        "/Low_Drivers/_Test"
    sys.path.append(
        BASE_PEATC_APP_PATH + "/_Test")
else:
    TEST_LOW_DRIVE = BASE_PEATC_APP_PATH + \
        "\\Low_Drivers\\_Test"
    sys.path.append(
        BASE_PEATC_APP_PATH + "\\_Test")

from GUI_Control import*

open(PEATC_CONFIG_DEB_LOG_PATH, 'w').close()
restorePoint = sys.stdout
sys.stdout = open(PEATC_CONFIG_DEB_LOG_PATH, 'a')

if PEATC_CONFIG_TEST_MODE is True:
    import _Test_RawVal_PEATC as Test_Vec

    if PEATC_CONFIG_CURR_OS == "Linux":
        TEST_RAW_PATH_TEMP_6 = BASE_PEATC_APP_PATH + "/_Test/_TestTempFile_6.tmp"
        TEST_RAW_PATH_TEMP_12 = BASE_PEATC_APP_PATH + "/_Test/_TestTempFile_12.tmp"
        TEST_RAW_PATH_TEMP_20 = BASE_PEATC_APP_PATH + "/_Test/_TestTempFile_20.tmp"

        TEST_GS_RAW_PATH = BASE_PEATC_APP_PATH + \
            "/../Low_Drivers/dev/xillybus_gs_raw_signal"
    else:
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

    if PEATC_CONFIG_TEST_MODE is True:
        GenRawFile(TEST_RAW_PATH_TEMP_6, Test_Vec.Test_AS_Raw_Data_6_month)
        GenRawFile(TEST_RAW_PATH_TEMP_12, Test_Vec.Test_AS_Raw_Data_12_month)
        GenRawFile(TEST_RAW_PATH_TEMP_20, Test_Vec.Test_AS_Raw_Data_20_month)

        with open(TEST_GS_RAW_PATH, 'wb') as FileGs_Raw:
            ByteSplit = [0, 0]
            Raw_Data_list = Test_Vec.Test_AS_Raw_Data_6_month
            for i in range(len(Raw_Data_list)):
                RawStream = Raw_Data_list[i]
                if RawStream <= 0xFF:
                    ByteSplit[0] = 0x0
                    ByteSplit[1] = RawStream
                elif RawStream <= 0xFFFF:
                    ByteSplit[0] = int((0xFF00 & RawStream) / 256)
                    ByteSplit[1] = 0xFF & RawStream

                FileGs_Raw.write(struct.pack(
                    'B' * 2, ByteSplit[0], ByteSplit[1]))

    GUI_Control()

    restorePoint = sys.stdout
    sys.stdout.close()
    sys.stdout = restorePoint
