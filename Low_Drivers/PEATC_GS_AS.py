import XillybusCom as Xillybus

class PEATC_Gs_As:

    '''
    Driver para el sistema Generate Signal, Analog Signal
    '''

    IsSingleton = None

    '''
    Implementación del patrón de diseño singelton, ya que se debe resguardar
    la manipulación de los archivos del Xillybus, ya que el manipular dichos
    archivos influye en señales de Hw generadas por el core del Xillibus
    '''

    def __new__(self):
        if self.IsSingleton is None:
            self.IsSingleton = super(PEATC_Gs_As, self).__new__(self)
        return self.IsSingleton

    '''
    Driver para el sistema Generate Signal, Analog Signal
    '''
    def Init_Test(TimeOut: int):
        Xillybus.memory_write()
