

PEATC_CONFIG_DEB_LOG_PATH = "Debug_Log_Output.txt"

PEATC_CONFIG_SignaldB = [30, 35, 40, 45, 50, 55, 60, 70]
PEATC_CONFIG_Latency = [100, 233, 120, 54]
PEATC_CONFIG_Freq = [50, 70, 100, 150]

'''!
Diccionario de diagnosticos resultantes
'''
PEATC_Conf_Diag_Dict = {
    "Normal values": 0,
    "Prolonged latency in Wave I": 1,
    "Prolonged latency between peaks I-III": 2,
    "Prolonged latency between peaks III-V": 3,
    "Prolonged latency between peaks IV-V and III-V ": 4,
    "Wave III absent with presence of I and V": 5,
    "Wave V absent with presence of I and III": 6,
    "Wave V absent with normal of I and III": 7,
    "Absence of waves": 8,
    "Excess in amplitude radius V / I": 9,
    "Absence of waves except I (and possibly II)": 10,
    "No Diagnostic": 11
}

PEATC_CONFIG_AMP_THRESHOLD = 10

PEATC_CONFIG_TIME_US_PER_SAMPLE = 100
