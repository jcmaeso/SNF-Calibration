import pyvisa
import time
from loguru import logger
from InstrumentControllers.antennaRF.antennaRFController import AntennaRFController

class E8362B(AntennaRFController):
    def __init__(self,addr="TCPIP0::A-E8362B-0392::5025::SOCKET") -> None:
        rm = pyvisa.ResourceManager()
        self.__visa_resource = rm.open_resource(addr)
        self.__visa_resource.timeout = 20000
        self.__visa_resource.read_termination = '\n'
        self.__visa_resource.write_termination = '\n'
        pna_id = self.__visa_resource.query("*IDN?")
        logger.info(pna_id)
        self.__visa_resource.write("FORM:DATA REAL,64")
        self.__pna_test = False #debug purposes
        if "E8362B" in pna_id:
            self.__pna_test = True
        self.__active_channels = []
        self.__n_trance = 1

    def __del__(self):
        self.__visa_resource.close()
    
    def create_measurement(self,name:str,param:str) -> int:
        cmd = "CALCulate{}:PARameter:DEFine '{}',{}".format(self.__n_measurements+1,name,param)
        self.__visa_resource.write(cmd)
        self.__n_measurements = self.__n_measurements+1
        self.__measurements_channels.append(name)
        self.__visa_resource.write("SENS{}:SWE:TRIG:POIN OFF".format(self.__n_measurements))
        return self.__n_measurements

    def setup_single_freq_cut(self,channel:int,frequency: float,points:float,if_bw=100) -> None:
        self.__visa_resource.write("SENS{}:SWE:TIME:AUTO 1".format(channel))
        self.__visa_resource.write("SENS{}:SWE:TRIG:POIN ON".format(channel))
        self.__visa_resource.write("SENS{}:SWE:MODE HOLD".format(channel))
        self.__visa_resource.write("SENS{}:FREQ:CENT {} GHz".format(channel,frequency))
        self.__visa_resource.write("SENS{}:FREQ:SPAN 0".format(channel))
        self.__visa_resource.write("SENS{}:SWE:POIN {}".format(channel,points))
        self.__visa_resource.write("SENS{}:BWID {}Hz".format(channel,if_bw))
        
        #self.__visa_resource.write("SENS{}:IF:SOUR:PATH 'R1', NORM".format(channel))
        #self.__visa_resource.write("SENS{}:IF:SOUR:PATH 'R2', NORM".format(channel))
        
        self.__visa_resource.write("SENS{}:IF:SOUR:PATH 'R1', Ext".format(channel))
        self.__visa_resource.write("SENS{}:IF:SOUR:PATH 'R2', Ext".format(channel))

        self.__visa_resource.write("SOUR:POW -5")

    def setup_multifreq_cut(self,channel:int,frequencies: float,points:float,if_bw=100) -> None:
        raise NotImplemented("This PNA does not support this feature")

    def setup_multi_freq_bypoint(self,channel,min_freq,max_freq,points,if_bw=100) -> None:
        #self.__visa_resource.write("SENS{}:SWE:TIME:AUTO 1".format(channel))
        #self.__visa_resource.write("SENS{}:SWE:MODE HOLD".format(channel))
        self.__visa_resource.write("SENS{}:FREQ:STAR {}GHz".format(channel,min_freq))
        self.__visa_resource.write("SENS{}:FREQ:STOP {}GHz".format(channel,max_freq))
        self.__visa_resource.write("SENS{}:SWE:POIN {}".format(channel,points))
        self.__visa_resource.write("SENS{}:BWID {}Hz".format(channel,if_bw))

        self.__visa_resource.write("SENS{}:IF:SOUR:PATH 'R1', Ext".format(channel))
        self.__visa_resource.write("SENS{}:IF:SOUR:PATH 'R2', Ext".format(channel))

        self.__visa_resource.write("SOUR:POW -5")


    def preset(self) -> None:
        self.__visa_resource.write('SYST:FPRESET')
        self.__n_measurements = 0
        self.__n_trance = 0
        self.__measurements_channels = []
    
    def enable_window(self) -> None:
        self.__visa_resource.write('DISP:WIND ON')

    def disable_window(self) -> None:
        self.__visa_resource.write('DISP:WIND OFF')
    
    def add_measurement_to_window(self,channel_name: str) -> None:
        self.__visa_resource.write("DISPlay:WINDow1:TRACe{}:FEED '{}'".format(self.__n_trance+1,channel_name))
        self.__n_trance = self.__n_trance + 1


    def config_manual_trigger(self) -> None:
        self.__visa_resource.write("TRIG:SOUR MAN")
        self.__visa_resource.write("TRIG:SCOP ALL")
    
    #Edge can be LOW or HIGH
    def config_external_trigger(self,edge = "HIGH") ->None:
        edge = edge.upper()
        if edge != "HIGH" and edge != "LOW":
            raise Exception("Invalid trigger level")
        
        self.__visa_resource.write("TRIG:SOUR EXT")
        self.__visa_resource.write("TRIG:LEV {}".format(edge))
        self.__visa_resource.write("TRIG:SCOP CURR")
        self.__visa_resource.write("SENSE:SWE:MODE CONT")
        self.__visa_resource.write("CONT:SIGN BNC1,TIENEGATIVE")
        

    def set_output_data_mode(self,mode : str) -> None:
        if mode == "double":
            self.__visa_resource.write("FORM:DATA REAL,64")
        elif mode == "ascii":
            self.__visa_resource.write("FORM:DATA ASCII")
        elif mode == "float":
            self.__visa_resource.write("FORM:DATA REAL,32")
        else:
            raise Exception("Unknown output format")

    def send_trigger(self) -> None:
        res = self.__visa_resource.query("INIT:IMM;*OPC?")

    def get_data_double(self,channel = 1):
        #Retrieve data into matrix
        #query if data completed
        sweep_finished = int(self.__visa_resource.query("STAT:OPER:DEV?"))
        if sweep_finished != 16:
            raise Exception("Sweep not finished exception")
        return self.__visa_resource.query_binary_values("CALC{}:DATA? SDATA".format(channel),is_big_endian=True,datatype="d")

    def get_data_float(self,channel = 1):
        #Retrieve data into matrix
        return self.__visa_resource.query_binary_values("CALC{}:DATA? SDATA".format(channel),is_big_endian=True,datatype="f")
    
    def clear_status(self):
        self.__visa_resource.write("*CLS")


    def reset_trigger(self):
        pass




if __name__ == "__main__":
    pna = E8362B()
    pna.preset()
    pna.enable_window()
    cp_channel = pna.create_measurement("CP","ar1")
    #pna.setup_single_freq_cut(cp_channel,30,6)
    pna.setup_multi_freq_bypoint(cp_channel,28,30,9,6)
    pna.add_measurement_to_window("CP")
    pna.config_external_trigger()
    for i in range(0,6):
        pna.send_trigger()
        time.sleep(1)
    exit()
