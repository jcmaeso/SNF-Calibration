import numpy as np
import numpy.typing as npt
import matlab.engine
import matplotlib.pyplot as plt
from  InstrumentControllers.antennaRF.N5264A import N5264A
from Beamformers.ControllerBoardInterface import ControllerBoardInterface
from loguru import logger
from InstrumentControllers.motor.orbit import Orbit
import scipy
import time


def calc(measured_data: npt.ArrayLike, phase_shifted: npt.ArrayLike) -> complex:
    measured_amplitude = abs(np.abs(measured_data))
    measured_phase = np.unwrap(np.angle(measured_data))

    delta_i = np.argmax(measured_amplitude)
    delta = -phase_shifted[delta_i]

    Emax = measured_amplitude[delta_i]
    Emin = np.min(measured_amplitude)

    phase_diff = np.max(measured_phase) - np.min(measured_phase)
    r = Emax / Emin
    Ga = (r - 1) / (r + 1)
    print(f"G:{Ga:.2f} Delta:{delta:.2f} Phase_Diff:{np.rad2deg(phase_diff):.2f}")

    delta = np.deg2rad(delta)
    rev_amp_sol1 = Ga / np.sqrt(1 + 2 * np.cos(delta) * Ga + Ga**2)
    rev_amp_sol2 = 1 / np.sqrt(1 + 2 * np.cos(delta) * Ga + Ga**2)

    rev_pha_sol1 = np.arctan2(np.sin(delta), np.cos(delta) + Ga)
    rev_pha_sol2 = np.arctan2(np.sin(delta), np.cos(delta) + 1 / Ga)

    if phase_diff < 180:
        return rev_amp_sol1 * np.exp(1j * rev_pha_sol1)

    return rev_amp_sol2 * np.exp(1j * rev_pha_sol2)


def antenna_power_on(board):
    #Disable all rails in order
    board.bsp_disable_rail(board.RAIL_1V)
    board.bsp_disable_rail(board.RAIL_3V3)
    board.bsp_disable_rail(board.RAIL_2V5)
    #Enable All rails in order
    board.bsp_enable_rail(board.RAIL_2V5)
    board.bsp_enable_rail(board.RAIL_1V)
    board.bsp_enable_rail(board.RAIL_3V3)

def antenna_power_off(board):
    #Disable all rails in order
    board.bsp_disable_rail(board.RAIL_1V)
    board.bsp_disable_rail(board.RAIL_3V3)
    board.bsp_disable_rail(board.RAIL_2V5)



def main_measurement():
    #Outputs
    outfilename = "broadside_uniform_cal_4_iter_10log"
    #Equipment setup
    antenna_com_port = "COM4"
    pna_ip_addr = "GPIB0::16::INSTR"
    orbit_gpib_addr = "GPIB0::4::INSTR"
    #Algorithm setup
    mapping = [6,7,4,5,2,3,0,1]
    initial_amp = [3,23,43,63,63,43,23,3]
    initial_phases = [0x00 for i in range(0,len(mapping))]
    #Cut configuration
    cut_axis = 1
    cut_speed = 70
    angular_init = -160
    angular_end = 160
    angular_increment = 1
    angular_points = len(np.arange(angular_init,angular_end,angular_increment))+1
    angular_direction = "f"

    #Start Connection with the VNA
    pna = N5264A(addr=pna_ip_addr)
    pna.preset()
    pna.setup_single_freq_cut(28,angular_points)
    pna.config_external_trigger()

    #Get Motor Controller
    motor_controller = Orbit.get_instance()

    #Init Antenna Controller
    board = ControllerBoardInterface(antenna_com_port)
    #Power antenna init sequence
    antenna_power_on(board)
    psc = board.bsp_monitor_rail(board.RAIL_1V)
    logger.info(f"Init Voltage: {psc[0]:.2f}V | Current: {psc[1]:.2f}A")
    #Init and Config Board
    board.board_complete_init()
    psc = board.bsp_monitor_rail(board.RAIL_1V)
    logger.info(f"Config Voltage: {psc[0]:.2f}V | Current: {psc[1]:.2f}A")
    #Program initial state
    for i in range(0,8):
        board.send_set_phase_amp_to_channel(mapping[i],initial_phases[i],initial_amp[i])

    psc = board.bsp_monitor_rail(board.RAIL_1V)
    logger.info(f"Setted state Voltage: {psc[0]:.2f}V | Current: {psc[1]:.2f}A")

    
    #Initial matrix for data
    measured_data = np.zeros(angular_points, dtype=complex)
            
    motor_controller.mode_register_movement(cut_axis,angular_init%360,angular_end%360,cut_speed,angular_increment,angular_direction)

    meas_trace = np.array(pna.get_data_double(),dtype=complex)
    measured_data = meas_trace[::2]+1j*meas_trace[1::2]
    angular_axis = np.arange(angular_init,angular_end+angular_increment,angular_increment)
    plt.plot(angular_axis, 20 * np.log10(np.abs(measured_data))-np.max(20 * np.log10(np.abs(measured_data))))
    scipy.io.savemat(f"{outfilename}.mat",{"theta": angular_axis,"measured_data":measured_data})
    time.sleep(1)
    motor_controller.mode_position_movement(int(cut_axis),0,'f',90)
    plt.show()







if __name__ == "__main__":
    main_measurement()
