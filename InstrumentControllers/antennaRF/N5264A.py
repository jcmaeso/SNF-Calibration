import pyvisa
import time
from loguru import logger


class N5264A():
    def __init__(self,addr="algoquetengoquemirar") -> None:
        rm = pyvisa.ResourceManager()
        self.__visa_resource = rm.open_resource(addr)
        self.__visa_resource.timeout = 20000
        pna_id = self.__visa_resource.query("*IDN?")
        print(pna_id)
        self.__visa_resource.write("FORM:DATA REAL,64")
        self.__pna_test = False #debug purposes
        if "E8362B" in pna_id:
            self.__pna_test = True

    def __del__(self):
        self.__visa_resource.close()

    def create_measurement(self, name: str, param: str) -> int:
        return super().create_measurement(name, param)

    #PNA del esférico
    def setup_single_freq_cut(self,frecuency,points,if_bw=100,power=12):
        self.multiplier_by_frequency(frecuency)

        self.__visa_resource.write("SENS:SWE:GRO:COUN 1")
        self.__visa_resource.write("SENS:FREQ:SPAN 0")
        self.__visa_resource.write("SENS:BWID {}Hz".format(if_bw))
        self.__visa_resource.write("SOUR:POW {}, 'PSG'".format(power))    
        self.__visa_resource.write("SENS:SWE:POIN {}".format(points))

        self.__visa_resource.write("SENS:FREQ:CENT {} GHz".format(frecuency))

    #PNA del esférico multifrecuencia
    def setup_multifreq_by_points(self,frequencies,npuntos):
        self.__visa_resource.write("TRIG:SEQ:SOUR MAN")
        self.__visa_resource.write("TRIG:SCOP CURR")

        self.__visa_resource.write("SENS:SWE:GRO:COUN 1")
        self.__visa_resource.write("SENS:SWE:POIN {}".format(npuntos))

        self.__visa_resource.write("SENS:FREQ:START {} GHz".format(frequencies[0]))
        self.__visa_resource.write("SENS:FREQ:STOP {} GHz".format(frequencies[1]))

        time.sleep(0.1)

    def config_manual_trigger(self):
        self.__visa_resource.write("TRIG:SEQ:SOUR MAN")
        self.__visa_resource.write("TRIG:SCOP CURR")
        self.__visa_resource.write("SENS:SWE:TRIG:MODE POINT")
    
    def config_external_trigger(self):
        self.__visa_resource.write("TRIG:SEQ:SOUR EXT")
        self.__visa_resource.write("TRIG:SCOP CURR")
        self.__visa_resource.write("SENS:SWE:TRIG:MODE POINT")
        self.__visa_resource.write("CONT:SIGN BNC1,TIENEGATIVE")




    def preset(self) -> None:
        self.__visa_resource.write('SYST:FPRESET')
        self.__n_measurements = 0
        self.__n_trance = 0
        self.__measurements_channels = []


    def multiplier(self,fact_mult,subarm):
        #offset calculation
        offset = -(subarm-1)/subarm*7.605634
        self.__visa_resource.write('SYST:FPRESET')
        self.__visa_resource.write("SYST:CONF:EDEV:STAT 'PSG', ON")
        self.__visa_resource.write("DISP:WIND1:STATE ON")
        self.__visa_resource.write("CALC:PAR:EXT 'S_21','B/A,PSG'")
        self.__visa_resource.write("DISP:WIND1:TRAC1:FEED 'S_21'")
        self.__visa_resource.write("SENS:FOM:DISP:SEL 'Primary'")

        self.__visa_resource.write("SENS:FOM:RANG4:COUP ON")
        self.__visa_resource.write("SENS:FREQ:CENT {}GHZ".format(10))
        self.__visa_resource.write("SENS:FREQ:SPAN 180")
        self.__visa_resource.write("SENS:FOM:RANG4:FREQ:DIV {}".format(fact_mult))
        self.__visa_resource.write("SENS:FOM:RANG3:FREQ:DIV {}".format(subarm))
        self.__visa_resource.write("SENS:FOM:RANG3:FREQ:OFFS {:8.6f} MHZ".format(offset))
        self.__visa_resource.write("SENS:FOM 1")
    
    def multiplier_by_frequency(self,frequency):
        if frequency in range(5,23):
            self.multiplier(1,1)
            print("Rango 5 20")
            return
        if frequency in range(23,42):
            self.multiplier(1,3)
            print("Rango 20-40")
            return
        elif frequency in range(42,60):
            self.multiplier(4,10)
            print("Rango 40-60")
            return
        elif frequency in range(60,75):
            self.multiplier(6,8)
            print(print("Rango 60-75"))
            return
        elif frequency in range(75,130):
            self.multiplier(6,18)
            print("Rango 75-130")
            return

    def enable_fifo(self):
        self.__visa_resource.write("SYST:FIFO ON")
        self.__visa_resource.write("SYST:FIFO:DATA:CLEAR")
        self.__visa_resource.write("FORM:DATA REAL,64")

    def read_fifo_len(self):
        return self.__visa_resource.query("SYST:FIFO:DATA:COUNT?")

        
    def read_fifo(self,points):
        return self.__visa_resource.query_binary_values("SYST:FIFO:DATA? {}".format(points),is_big_endian=True,datatype="d")
        
    def send_trigger(self):
        res = self.__visa_resource.query("INIT:IMM;*OPC?")
    
    def get_data_double(self):
        #Retrieve data into matrix
        return self.__visa_resource.query_binary_values("CALC:DATA? SDATA",is_big_endian=True,datatype="d")
        

if __name__ == "__main__":
    pna = PNA_Controller("GPIB0::16::INSTR")
    npuntos_fifo = int(pna.read_fifo_len())
    measure = pna.read_fifo(npuntos_fifo)
    with open("multi_pna","w") as f:
        for i in range(0,len(measure),2):
            f.write("{:.10f}\n".format(complex(measure[i],measure[i+1])))
    exit()
    pna.multiplier(6,18,-7.18309877777778)
    n_puntos = 5;
    #pna.setup_cut_pna_x(82,n_puntos)
    pna.setup_multifreq2([75,80],6)
    pna.enable_fifo()
    #pna.setup_multifreq([75,80,90,100,110])
    time.sleep(1)
    for i in range(0,n_puntos):
        pna.trigger()
        print("Trigger")
        time.sleep(2)
    print(pna.read_fifo_len())