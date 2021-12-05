'''!
Configuración de la aplicación
'''
PEATC_CONFIG_DEB_LOG_PATH = "Debug_Log_Output.txt"

PEATC_CONFIG_CURR_OS = "Windows"#"Linux"
PEATC_CONFIG_TEST_MODE = True

'''!
Configuración parametros de la prueba de PEATC
'''

PEATC_CONFIG_SignaldB = [30, 40, 50]
PEATC_CONFIG_Latency = [100, 233, 120, 54]
PEATC_CONFIG_Freq = [50, 70, 100, 150]

'''!
Configuración parametros de sensasdo de las
señales de PEATC
'''
PEATC_CONFIG_FIRST_WAVE_MIN_ = 0
PEATC_CONFIG_FIRST_WAVE_MAX_ = 2000

PEATC_CONFIG_THIRD_WAVE_MIN_ = 3500
PEATC_CONFIG_THIRD_WAVE_MAX_ = 4500

PEATC_CONFIG_FIFTH_WAVE_MIN_ = 5500
PEATC_CONFIG_FIFTH_WAVE_MAX_ = 7000


PEATC_CONFIG_AMP_THRESHOLD = 10
PEATC_CONFIG_TIME_US_PER_SAMPLE = 100


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
