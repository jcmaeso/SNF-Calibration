import abc

class AntennaRFController(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def create_measurement(self,name:str,param:str) -> int:
        pass
    
    @abc.abstractmethod
    def setup_single_freq_cut(self,channel:int,frequency: float,points:float,if_bw=100) -> None:
        pass
    
    @abc.abstractmethod
    def setup_multifreq_cut(self,channel:int,frequencies: float,points:float,if_bw=100) -> None:
        pass

    @abc.abstractmethod
    def setup_multi_freq_bypoint(self,channel,min_freq,max_freq,points,if_bw=100) -> None:
        pass

    @abc.abstractmethod
    def preset(self) -> None:
        pass

    @abc.abstractmethod
    def enable_window(self) -> None:
        pass

    @abc.abstractmethod
    def disable_window(self) -> None:
        pass
    
    @abc.abstractmethod
    def add_measurement_to_window(self,channel_name: str) -> None:
        pass

    @abc.abstractmethod
    def config_manual_trigger(self):
        pass

    @abc.abstractmethod
    def config_external_trigger(self):
        pass

    @abc.abstractmethod
    def set_output_data_mode(self,mode : str) -> None:
        pass
    
    @abc.abstractmethod
    def send_trigger(self) -> None:
        pass


    @abc.abstractmethod
    def get_data_double(self,channel):
        pass

    @abc.abstractmethod 
    def get_data_float(self,channel):
        pass

    @abc.abstractmethod 
    def clear_status(self):
        pass

    @abc.abstractmethod 
    def reset_trigger(self):
        pass


