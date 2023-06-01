import serial
import time

class SerialControllerBoardInterface():

    def __init__(self):
        #define constants for byte package size
        self._header_len = 5
        #define constants for masking
        self._rsp_mask_master = 0x50
        self._rsp_mask_status = 0xAA
        self._rsp_mask_data = 0xBB
        self._rsp_codes = {
            1:"ACK",
            2:"Unknown Group",
            3:"Unknown Command",
            4:"Invalid Argument Length",
            5:"Invalid Argument",
            6:"Error processing command",
        }
        self._serial_port = None

    def open_port(self,serial_port_name):
        if self._serial_port is not None:
            return
        try:
            self._serial_port = serial.Serial(serial_port_name,115200)
        except:
            time.sleep(10)
            self._serial_port = serial.Serial(serial_port_name,115200)

    def close_port(self):
        if self._serial_port is None:
            return
        self._serial_port.close()
        self._serial_port = None

    def build_command(self,group,command,data = []):
        header = []
        if type(data) is int:
            data = [data]
        elif type(data) is not list:
            raise Exception("Data format is not correct (list or str)")
        
        header.append(0xAF)
        header.append(len(data))
        header.append(0xFF)
        header.append(group)
        header.append(command)
        return bytearray(header + data)
            
    
    def send_command(self,cmd_bin,rsp_len):
        self._serial_port.write(cmd_bin)
        bytes_read = []
        try:
            bytes_read = self._serial_port.read(rsp_len)
        except:
            print("Error reading bytes")

        if len(bytes_read) < rsp_len:
            print("Error reading, len not matched")
            return

        if bytes_read[0] != self._rsp_mask_master:
            raise Exception("Master Mask Error")
        if bytes_read[2] == self._rsp_mask_status:
            #Check if ACK(1) or Error 
            if bytes_read[1] != 1:
                raise Exception(self._rsp_codes[bytes_read[1]] if bytes_read[1] in self._rsp_codes[bytes_read[1]] else "Unkwown error code" )
        
            return []

        elif bytes_read[2] == self._rsp_mask_data:
            #Check Len
            if int(bytes_read[1]) != rsp_len - self._header_len:
                raise Exception("Length provided does not match received")
            return bytes_read[self._header_len:len(bytes_read)]
        else:
            raise Exception("Unknown response")
