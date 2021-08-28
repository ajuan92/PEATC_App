import os
import sys
import struct

import multiprocessing as mprocess
from multiprocessing import Array

_TEST_PATH = os.getcwd()
BASE_CB_PATH = _TEST_PATH + "\\.."
BASE_PEATC_APP_PATH = BASE_CB_PATH + "\\.."

sys.path.append(
    BASE_CB_PATH)

TEST_LOW_DRIVE = BASE_PEATC_APP_PATH + \
    "\\Low_Drivers\\_Test"

sys.path.append(
    TEST_LOW_DRIVE)

import _Test_RawVal_PEATC as Test_Vec
import PEATC_Analyze as Analyze
import PEATC_Control as Ctrl

TEST_RAW_PATH_TEMP_6 = _TEST_PATH + "\\_TestTempFile_6.tmp"
TEST_RAW_PATH_TEMP_12 = _TEST_PATH + "\\_TestTempFile_12.tmp"
TEST_RAW_PATH_TEMP_20 = _TEST_PATH + "\\_TestTempFile_20.tmp"


TEST_GS_START_PATH = BASE_PEATC_APP_PATH + \
    "\\Low_Drivers\\dev\\xillybus_gs_start_test"
TEST_GS_RAW_PATH = BASE_PEATC_APP_PATH + \
    "\\Low_Drivers\\dev\\xillybus_gs_raw_signal"

TEST_RN_DIAG_PARAM = BASE_PEATC_APP_PATH + \
    "\\Low_Drivers\\dev\\xillybus_rn_diag_param"
TEST_RN_DIAG_RESULT = BASE_PEATC_APP_PATH + \
    "\\Low_Drivers\\dev\\xillybus_rn_diag_result"


# -------------------------Utilidades---------------------------------

Cmd_Template = {
    "Cmd": 1,
    "Gs_SignaldB": 1,
    "Gs_Latency": 2,
    "Gs_Polarity": 3,
    "Gs_Freq": 4,
}

Cmd_Test_P1 = {
    "Gs_SignaldB": 70,
    "Gs_Latency": 100,
    "Gs_Polarity": 1,
    "Gs_Freq": 60,
}

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

# -------------------------PRE-TEST---------------------------------


with open(TEST_GS_START_PATH, 'w') as FileGs_Start:
    pass

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

with open(TEST_RN_DIAG_PARAM, 'wb') as FileDiag_Param:
    pass

with open(TEST_RN_DIAG_RESULT, 'wb') as FileDiag_Raw:
    FileDiag_Raw.write(struct.pack('b' * 4, 0, 0, 0, 0x5))
    pass

GenRawFile(TEST_RAW_PATH_TEMP_6, Test_Vec.Test_AS_Raw_Data_6_month)
GenRawFile(TEST_RAW_PATH_TEMP_12, Test_Vec.Test_AS_Raw_Data_12_month)
GenRawFile(TEST_RAW_PATH_TEMP_20, Test_Vec.Test_AS_Raw_Data_20_month)

WavePEATC = []
FullWaveData = []

if __name__ == '__main__':

    Ctrl_Cmd_output, Ctrl_Cmd_input = mprocess.Pipe(False)
    Ctrl_Result_output, Ctrl_Result_input = mprocess.Pipe(False)

    Ctrl_State = Array('i', range(1))

    Diag_Table_output, Diag_Table_input = mprocess.Pipe(False)
    Diag_Result_output, Diag_Result_input = mprocess.Pipe(False)

    Diag_State = Array('i', range(1))

    Ctrl_Block = Ctrl.PEATC_Control()

    Ctrl_Task = mprocess.Process(target=Ctrl_Block.ControlHandler, args=(
        Ctrl_Cmd_output, Ctrl_Result_input, Ctrl_State),)

    Diag_Task = mprocess.Process(target=Ctrl_Block.DiagHandler, args=(
        Diag_Table_output, Diag_Result_input, Diag_State),)

    Ctrl_Task.daemon = True
    Ctrl_Task.start()

    Diag_Task.daemon = True
    Diag_Task.start()

# ---------------------------TEST-----------------------------------

    print("----------Test_CB_1.1 Start---------")

    Analyze.AnalyzeSignal("_TestTempFile_6.tmp")

    print("----------Test_CB_1.1 End-----------")
    print("----------Test_CB_1.2 Start---------")

    Analyze.AnalyzeSignal("_TestTempFile_12.tmp")

    print("----------Test_CB_1.2 End-----------")
    print("----------Test_CB_1.3 Start---------")

    Analyze.AnalyzeSignal("_TestTempFile_20.tmp")

    print("----------Test_CB_1.3 End-----------")
    print("----------Test_CB_1 End-------------")
    print("----------Test_CB_2 Start-----------")

    Ctrl_Cmd_input.send(Cmd_Template)
    Ctrl_Task.join(5)
    print("_Test -- " + str(Ctrl_State[0]))
    print("---")
    WavePEATC, FullWaveData = Ctrl_Result_output.recv()
    print(WavePEATC)
    print(FullWaveData)

    print("----------Test_CB_2 End-------------")
    print("----------Test_CB_3 Start-----------")

    Diag_Table_input.send([25, [WavePEATC]])
    Diag_Task.join(5)
    print("***")
    print(Diag_Result_output.recv())

    print("----------Test_CB_3 End-------------")
    print("----------Test_CB_4 Start-----------")

    GenRawFile(TEST_GS_RAW_PATH, Test_Vec.Test_AS_Raw_Data_6_month)
    Ctrl_Cmd_input.send(Cmd_Template)
    Ctrl_Task.join(5)
    WavePEATC1, FullWaveData1 = Ctrl_Result_output.recv()
    print(WavePEATC1)
    print(FullWaveData1)
    print("---")
    GenRawFile(TEST_GS_RAW_PATH, Test_Vec.Test_AS_Raw_Data_12_month)
    Ctrl_Cmd_input.send(Cmd_Template)
    Ctrl_Task.join(5)
    WavePEATC2, FullWaveData2 = Ctrl_Result_output.recv()
    print(WavePEATC2)
    print(FullWaveData2)
    print("---")
    GenRawFile(TEST_GS_RAW_PATH, Test_Vec.Test_AS_Raw_Data_20_month)
    Ctrl_Cmd_input.send(Cmd_Template)
    Ctrl_Task.join(5)
    WavePEATC3, FullWaveData3 = Ctrl_Result_output.recv()
    print(WavePEATC3)
    print(FullWaveData3)
    print("---")
    GenRawFile(TEST_GS_RAW_PATH, Test_Vec.Test_AS_Raw_Data_12_month)
    Ctrl_Cmd_input.send(Cmd_Template)
    Ctrl_Task.join(5)
    WavePEATC2, FullWaveData2 = Ctrl_Result_output.recv()
    print(WavePEATC2)
    print(FullWaveData2)
    print("---")

    Diag_Table_input.send([25, [WavePEATC1, WavePEATC2, WavePEATC3]])
    Diag_Task.join(5)
    print("_Test -- " + str(Diag_State[0]))
    print("***")
    print(Diag_Result_output.recv())

    print("----------Test_CB_4 End-------------")
    print("----------Test_CB_5 Start-------------")

    print("----------Test_CB_5 End-------------")

# -------------------------POST-TEST---------------------------------
    with open(TEST_GS_START_PATH, 'r') as FileGs_Start:
        pass

    with open(TEST_GS_RAW_PATH, 'r') as FileGs_Raw:
        pass

    with open(TEST_RN_DIAG_PARAM, 'r') as FileDiag_Param:
        pass

    with open(TEST_RN_DIAG_RESULT, 'r') as FileDiag_Param:
        pass
