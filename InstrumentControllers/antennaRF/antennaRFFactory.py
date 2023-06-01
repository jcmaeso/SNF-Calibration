from loguru import logger
import sys

from typing_extensions import Self
from InstrumentControllers.antennaRF.pna_E8362B import E8362B
from InstrumentControllers.antennaRF.N5264A import N5264A

from InstrumentControllers.antennaRF.antennaRFController import AntennaRFController


class ARFCFactory():
    __instance = None
    __rfController : AntennaRFController = None

    def __init__(self):
        """ Virtually private constructor. """
        if ARFCFactory.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            ARFCFactory.__instance = self

    @staticmethod
    def get_instance():
        """ Static access method. """
        if ARFCFactory.__instance == None:
            ARFCFactory()
        return ARFCFactory.__instance
        
    def get_controller(self) -> AntennaRFController:
        if self.__rfController == None:
            raise Exception("Controller not initialized")
        return self.__rfController

    def create_antennaRFController(self,id:str,addr="") -> AntennaRFController:
        if self.__rfController == None:
            if id == 'ES8362B':
                self.__rfController = E8362B() if addr == "" else E8362B(addr)
            elif id=="N5264A":
                self.__rfController = N5264A() if addr == "" else E8362B(addr)
            else:
                raise Exception("Unknown device")
    
    def delete_antennaRFController(self):
        if self.__rfController != None:
            del self.__rfController
            self.__rfController = None
 