import sys
sys.path.append(
    "E:\\ARCHIVOS_Y_DOCUMENTOS\\01_Tesis_Local\\PEATC_App\\Control_Block")

import PEATC_Analyze

#-------------------------PRE-TEST---------------------------------


#---------------------------TEST-----------------------------------

print("----------Test_CB_1 Start---------")

PEATC_Analyze.AnalyzeSignal("_TestTempFile_6.tmp")

print("----------Test_CB_1 End-----------")
print("----------Test_CB_1 Start---------")

PEATC_Analyze.AnalyzeSignal("_TestTempFile_12.tmp")

print("----------Test_CB_1 End-----------")
print("----------Test_CB_1 Start---------")

PEATC_Analyze.AnalyzeSignal("_TestTempFile_20.tmp")

print("----------Test_CB_1 End-----------")


#-------------------------POST-TEST---------------------------------