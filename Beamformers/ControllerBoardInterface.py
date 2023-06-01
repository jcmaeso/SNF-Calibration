import os
import serial
import pyvisa
import time
from datetime import datetime
from SerialControllerBoardInterface import SerialControllerBoardInterface
import struct
from loguru import logger

class ControllerBoardInterface():
    def __init__(self,port_name):
        self._serial_ctrl = SerialControllerBoardInterface()
        self.RAIL_1V = 0
        self.RAIL_1V2 = 1
        self.RAIL_3V3 = 2
        self.RAIL_2V5 = 3
        self._port_name = port_name

    def board_complete_init(self):
        self._serial_ctrl.open_port(self._port_name)
        self._serial_ctrl.send_command(self._serial_ctrl.build_command(0x01,0x05),5)
        self._serial_ctrl.send_command(self._serial_ctrl.build_command(0x01,0x03,0xFF),5)
        self._serial_ctrl.close_port()

    def board_complete_init_rx(self):
        self._serial_ctrl.open_port(self._port_name)
        self._serial_ctrl.send_command(self._serial_ctrl.build_command(0x01,0x0C),5)
        self._serial_ctrl.send_command(self._serial_ctrl.build_command(0x01,0x03,0xFF),5)
        self._serial_ctrl.close_port()
    
    def board_complete_init_rx_channel(self,channel):
        self._serial_ctrl.open_port(self._port_name)
        self._serial_ctrl.send_command(self._serial_ctrl.build_command(0x01,0x0D,channel),5)
        self._serial_ctrl.send_command(self._serial_ctrl.build_command(0x01,0x03,0x01 << channel),5)
        self._serial_ctrl.close_port()

    def enable_all_channels(self):
        self._serial_ctrl.open_port(self._port_name)
        self._serial_ctrl.send_command(self._serial_ctrl.build_command(0x01,0x03,0xFF),5)
        self._serial_ctrl.close_port()

    def turn_board_on(self):
        self._serial_ctrl.open_port(self._port_name)
        self._serial_ctrl.send_command(self._serial_ctrl.build_command(0x01,0x00),5)
        self._serial_ctrl.close_port()

    def init_chip(self):
        self._serial_ctrl.open_port(self._port_name)
        self._serial_ctrl.send_command(self._serial_ctrl.build_command(0x01,0x05),5)
        self._serial_ctrl.close_port()

    def send_set_phase_amp_to_channel(self,channel,phase,amp):
        self._serial_ctrl.open_port(self._port_name)
        self._serial_ctrl.send_command(self._serial_ctrl.build_command(0x01,0x08,[channel,phase,amp]),5)
        self._serial_ctrl.close_port()

    def send_phases_amps_once(self,phases,amps):
        self._serial_ctrl.open_port(self._port_name)
        self._serial_ctrl.send_command(self._serial_ctrl.build_command(0x01,0x09,phases+amps),5)
        self._serial_ctrl.close_port()

    def send_set_phase_amp_to_zero(self):
        some_zeroes_phase = [0 for i in range(0,8)]
        some_zeroes_amp = [0x3F for i in range(0,8)]
        self.send_phases_amps_once(some_zeroes_phase,some_zeroes_amp)
    
    def open_comm_port(self):
        self._serial_ctrl.open_port(self._port_name)
    
    def close_comm_port(self):
        self._serial_ctrl.close_port()

    def send_phases_amps_mutiple(self,phases,amps):
        self._serial_ctrl.send_command(self._serial_ctrl.build_command(0x01,0x09,phases+amps),5)
    
    def enable_channels(self,channels):
        self._serial_ctrl.open_port(self._port_name)
        self._serial_ctrl.send_command(self._serial_ctrl.build_command(0x01,0x03,channels),5)
        self._serial_ctrl.close_port()

    def bsp_enable_rail(self,rail):
        self._serial_ctrl.open_port(self._port_name)
        self._serial_ctrl.send_command(self._serial_ctrl.build_command(0x00,0x00,rail),5)
        self._serial_ctrl.close_port()
    
    def bsp_disable_rail(self,rail):
        self._serial_ctrl.open_port(self._port_name)
        self._serial_ctrl.send_command(self._serial_ctrl.build_command(0x00,0x01,rail),5)
        self._serial_ctrl.close_port()

    def bsp_monitor_rail(self,rail) -> tuple[float,float]:
        self._serial_ctrl.open_port(self._port_name)
        read_data = self._serial_ctrl.send_command(self._serial_ctrl.build_command(0x00,0x02,rail),13) 
        self._serial_ctrl.close_port()
        return (struct.unpack('f',read_data[0:4])[0],struct.unpack('f',read_data[4:])[0])

if __name__ == "__main__":
    board = ControllerBoardInterface("COM9")
    logger_filename = "SNF-1GRADO.psc"
    logger.add(logger_filename)
    start_time = time.time()

    board.bsp_disable_rail(board.RAIL_1V)
    board.bsp_disable_rail(board.RAIL_3V3)
    board.bsp_disable_rail(board.RAIL_2V5)


    board.bsp_enable_rail(board.RAIL_2V5)
    board.bsp_enable_rail(board.RAIL_1V)
    board.bsp_enable_rail(board.RAIL_3V3)
    psc = board.bsp_monitor_rail(board.RAIL_1V)
    logger.info(f"{time.time()-start_time};{psc[0]:.2f};{psc[1]:.2f}")
    board.board_complete_init()
    psc = board.bsp_monitor_rail(board.RAIL_1V)
    logger.info(f"{time.time()-start_time};{psc[0]:.2f};{psc[1]:.2f}")


    mapping = [6,7,4,5,2,3,0,1]
    #amp = [0x0,0x0,0x0,0x3F,0x0,0x0,0x0,0x0]
    amp = [0x3F,0x3F,0x3F,0x3F,0x3F,0x3F,0x3F,0x3F]
    phase = [0,0,0,0,0,0,0,0]
    #phase = [0,5,11,16,21,27,32,38] #-10 grados
    #phase = [0,11,21,32,42,53,63,10] #-20 grados
    #phase = [0,15,31,46,62,13,29,44] #-30 grados
    #phase = [0,20,40,60,15,35,55,11] #-40 grados
    #phase = [0,24,47,7,31,54,14,38] #-50 grados

    for i in range(0,8):
        board.send_set_phase_amp_to_channel(mapping[i],phase[i],amp[i])

    while(True):
        psc = board.bsp_monitor_rail(board.RAIL_1V)
        logger.info(f"{time.time()-start_time};{psc[0]:.2f};{psc[1]:.2f}")
        time.sleep(2)



    
