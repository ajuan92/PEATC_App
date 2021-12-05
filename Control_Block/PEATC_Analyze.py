import array
import os
import sys

PEATC_ANALYZE_PATH = os.path.dirname(os.path.realpath(__file__))

try:
    CONFIG_DRIVE_PATH = PEATC_ANALYZE_PATH + "\\..\\Config"
    sys.path.append(
        CONFIG_DRIVE_PATH)
except ImportError:
    print(CONFIG_DRIVE_PATH)
else:
    CONFIG_DRIVE_PATH = PEATC_ANALYZE_PATH + "/../Config"
    sys.path.append(
        CONFIG_DRIVE_PATH)

from PEATC_Config import*


def TwoComplement(Value):
    '''!
    Convierte un valor de 16 bits a su representación
    en entero con complemento a 2

    @param Value Valor a convertir a complemento a 2
    '''
    twos_complement = 0
    if Value > 0x7FFF:
        flipped_binary_number = Value - 65536
        twos_complement = flipped_binary_number
    else:
        twos_complement = Value
    return twos_complement


def AnalyzeSignal(Signal_file: str):
    '''!
    Analiza los datos crudos de la señal de PEATC

    @param Signal_file dirección del archivo donde se encuentra
    la señal cruda prepocesada de la señal de PEATC
    '''
    with open(Signal_file, 'rb') as RawSignal_File:
        ReadData = RawSignal_File.read()
        DataCapture = array.array('i')
        TimeCapture = array.array('i')

        TimeIndex = 0
        Byte2Word = 0
        Index = 0
        while Index < (len(ReadData) - 1):
            Byte2Word = (ReadData[Index] * 256) + ReadData[Index + 1]
            Index += 2
            Byte2Word = TwoComplement(Byte2Word)
            DataCapture.append(Byte2Word)
            TimeCapture.append(TimeIndex * PEATC_CONFIG_TIME_US_PER_SAMPLE)
            TimeIndex += 1

    WaveAmpLat = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]

    RawWave = [[], [], [], [], []]
    TimeWave = [[], [], [], [], []]

    WaveCount = 0

    for i in range(len(DataCapture)-1):
        if DataCapture[i] >= PEATC_CONFIG_AMP_THRESHOLD:
            RawWave[WaveCount].append(DataCapture[i])
            TimeWave[WaveCount].append(TimeCapture[i])

            if DataCapture[i + 1] < PEATC_CONFIG_AMP_THRESHOLD - 1:
                WaveCount = WaveCount + 1

    print("===" + "PEATC_Analyze" + "===")
    print("Numero de ondas identificadas")
    print(WaveCount)
    print("Ondas identificadas")
    print(RawWave)
    print("====================\n")

    SignalWaveIndex = [0, 0, 0, 0, 0]

    InitFilterIndex = 0
    FilterIndex = 0
    i = 0

    print("\n===" + "PEATC_Analyze" + "===")
    print("Ondas y latencias")

    while i < len(WaveAmpLat):

        FilterIndex = InitFilterIndex

        while FilterIndex < len(RawWave):

            if len(RawWave[FilterIndex]) is not 0:
                SignalWaveIndex = RawWave[FilterIndex].index(
                    max(RawWave[FilterIndex]))

                if ((PEATC_CONFIG_FIRST_WAVE_MIN_ <= TimeWave[FilterIndex][SignalWaveIndex])
                        and (TimeWave[FilterIndex][SignalWaveIndex] <= PEATC_CONFIG_FIRST_WAVE_MAX_)):

                    print(str(RawWave[FilterIndex]) + " 0-> " +
                          str(TimeWave[FilterIndex][SignalWaveIndex]))

                    if (WaveAmpLat[0][0] < RawWave[FilterIndex][SignalWaveIndex]):

                        WaveAmpLat[0] = [
                            RawWave[FilterIndex][SignalWaveIndex], TimeWave[FilterIndex][SignalWaveIndex]]

                    InitFilterIndex = FilterIndex + 1
                    FilterIndex = len(RawWave)

                elif ((PEATC_CONFIG_FIRST_WAVE_MAX_ < TimeWave[FilterIndex][SignalWaveIndex])
                      and (TimeWave[FilterIndex][SignalWaveIndex] < PEATC_CONFIG_THIRD_WAVE_MIN_)):

                    print(str(RawWave[FilterIndex]) + " 1-> " +
                          str(TimeWave[FilterIndex][SignalWaveIndex]))

                    if (WaveAmpLat[1][0] < RawWave[FilterIndex][SignalWaveIndex]):
                        WaveAmpLat[1] = [
                            RawWave[FilterIndex][SignalWaveIndex], TimeWave[FilterIndex][SignalWaveIndex]]

                    InitFilterIndex = FilterIndex + 1
                    FilterIndex = len(RawWave)

                elif ((PEATC_CONFIG_THIRD_WAVE_MIN_ <= TimeWave[FilterIndex][SignalWaveIndex])
                      and (TimeWave[FilterIndex][SignalWaveIndex] <= PEATC_CONFIG_THIRD_WAVE_MAX_)):

                    print(str(RawWave[FilterIndex]) + " 2-> " +
                          str(TimeWave[FilterIndex][SignalWaveIndex]))

                    if (WaveAmpLat[2][0] < RawWave[FilterIndex][SignalWaveIndex]):
                        WaveAmpLat[2] = [
                            RawWave[FilterIndex][SignalWaveIndex], TimeWave[FilterIndex][SignalWaveIndex]]

                    InitFilterIndex = FilterIndex + 1
                    FilterIndex = len(RawWave)

                elif ((PEATC_CONFIG_THIRD_WAVE_MAX_ < TimeWave[FilterIndex][SignalWaveIndex])
                      and (TimeWave[FilterIndex][SignalWaveIndex] < PEATC_CONFIG_FIFTH_WAVE_MIN_)):

                    print(str(RawWave[FilterIndex]) + " 3-> " +
                          str(TimeWave[FilterIndex][SignalWaveIndex]))

                    if (WaveAmpLat[3][0] < RawWave[FilterIndex][SignalWaveIndex]):
                        WaveAmpLat[3] = [
                            RawWave[FilterIndex][SignalWaveIndex], TimeWave[FilterIndex][SignalWaveIndex]]

                    InitFilterIndex = FilterIndex + 1
                    FilterIndex = len(RawWave)

                elif ((PEATC_CONFIG_FIFTH_WAVE_MIN_ <= TimeWave[FilterIndex][SignalWaveIndex])
                      and (TimeWave[FilterIndex][SignalWaveIndex] <= PEATC_CONFIG_FIFTH_WAVE_MAX_)):

                    print(str(RawWave[FilterIndex]) + " 4-> " +
                          str(TimeWave[FilterIndex][SignalWaveIndex]))

                    if (WaveAmpLat[4][0] < RawWave[FilterIndex][SignalWaveIndex]):
                        WaveAmpLat[4] = [
                            RawWave[FilterIndex][SignalWaveIndex], TimeWave[FilterIndex][SignalWaveIndex]]

                    InitFilterIndex = FilterIndex + 1
                    FilterIndex = len(RawWave)

                else:
                    WaveAmpLat[i].append(0)
                    WaveAmpLat[i].append(0)

            FilterIndex = FilterIndex + 1

        i = i + 1
    print("Amp's & Lat's")
    print(WaveAmpLat)
    print("====================\n")
    sys.stdout.flush()
    return WaveAmpLat, DataCapture
