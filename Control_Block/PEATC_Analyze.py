import array

PEATC_CONFIG_AMP_THRESHOLD = 10

PEATC_CONFIG_TIME_US_PER_SAMPLE = 100


FIRST_WAVE_MIN_ = 0
FIRST_WAVE_MAX_ = 2000

THIRD_WAVE_MIN_ = 3500
THIRD_WAVE_MAX_ = 4500

FIFTH_WAVE_MIN_ = 5500
FIFTH_WAVE_MAX_ = 7000


def TwoComplement(Value):
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

    WaveAmpLat = [[], [], [], [], []]

    RawWave = [[], [], [], [], []]
    TimeWave = [[], [], [], [], []]

    WaveCount = 0

    for i in range(len(DataCapture)):
        print(DataCapture[i]) #problema al detectar bajada, no detecna negativos buscar otra forma de evaluar
        if DataCapture[i] > PEATC_CONFIG_AMP_THRESHOLD:

            RawWave[WaveCount].append(DataCapture[i])
            TimeWave[WaveCount].append(TimeCapture[i])

            print(DataCapture[i + 1])
            if DataCapture[i + 1] < PEATC_CONFIG_AMP_THRESHOLD - 1:
                WaveCount = WaveCount + 1
        

    print(WaveCount)
    print("--")
    print(RawWave)

    SignalWaveIndex = [0, 0, 0, 0, 0]

    InitFilterIndex = 0
    FilterIndex = 0
    i = 0

    while i < len(WaveAmpLat):

        FilterIndex = InitFilterIndex

        while FilterIndex < len(RawWave):

            if len(RawWave[FilterIndex]) is not 0:
                SignalWaveIndex = RawWave[FilterIndex].index(
                    max(RawWave[FilterIndex]))

                if (FIRST_WAVE_MIN_ <= TimeWave[FilterIndex][SignalWaveIndex]) and (TimeWave[FilterIndex][SignalWaveIndex] <= FIRST_WAVE_MAX_):

                    WaveAmpLat[0].append(RawWave[FilterIndex][SignalWaveIndex])
                    WaveAmpLat[0].append(
                        TimeWave[FilterIndex][SignalWaveIndex])
                    InitFilterIndex = FilterIndex + 1
                    FilterIndex = len(RawWave)

                elif (FIRST_WAVE_MAX_ <= TimeWave[FilterIndex][SignalWaveIndex]) and (TimeWave[FilterIndex][SignalWaveIndex] <= THIRD_WAVE_MIN_):
                    WaveAmpLat[1].append(RawWave[FilterIndex][SignalWaveIndex])
                    WaveAmpLat[1].append(
                        TimeWave[FilterIndex][SignalWaveIndex])
                    InitFilterIndex = FilterIndex + 1
                    FilterIndex = len(RawWave)

                elif (THIRD_WAVE_MIN_ <= TimeWave[FilterIndex][SignalWaveIndex]) and (TimeWave[FilterIndex][SignalWaveIndex] <= THIRD_WAVE_MAX_):

                    WaveAmpLat[2].append(RawWave[FilterIndex][SignalWaveIndex])
                    WaveAmpLat[2].append(
                        TimeWave[FilterIndex][SignalWaveIndex])
                    InitFilterIndex = FilterIndex + 1
                    FilterIndex = len(RawWave)

                elif (THIRD_WAVE_MAX_ <= TimeWave[FilterIndex][SignalWaveIndex]) and (TimeWave[FilterIndex][SignalWaveIndex] <= FIFTH_WAVE_MIN_):

                    WaveAmpLat[3].append(RawWave[FilterIndex][SignalWaveIndex])
                    WaveAmpLat[3].append(
                        TimeWave[FilterIndex][SignalWaveIndex])
                    InitFilterIndex = FilterIndex + 1
                    FilterIndex = len(RawWave)

                elif (FIFTH_WAVE_MIN_ <= TimeWave[FilterIndex][SignalWaveIndex]) and (TimeWave[FilterIndex][SignalWaveIndex] <= FIFTH_WAVE_MAX_):

                    WaveAmpLat[4].append(RawWave[FilterIndex][SignalWaveIndex])
                    WaveAmpLat[4].append(
                        TimeWave[FilterIndex][SignalWaveIndex])
                    InitFilterIndex = FilterIndex + 1
                    FilterIndex = len(RawWave)

                else:
                    WaveAmpLat[i].append(0)
                    WaveAmpLat[i].append(0)
            FilterIndex = FilterIndex + 1
        i = i + 1
    print(WaveAmpLat)
