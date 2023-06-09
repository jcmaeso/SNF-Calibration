import numpy as np
import numpy.typing as npt
import matlab.engine
import matplotlib.pyplot as plt
from  InstrumentControllers.antennaRF.N5264A import N5264A
from Beamformers.ControllerBoardInterface import ControllerBoardInterface
from loguru import logger
import scipy


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
    #Equipment setup
    antenna_com_port = "COM4"
    pna_ip_addr = "GPIB0::16::INSTR"
    orbit_gpib_addr = ""
    #Algorithm setup
    outfile = "ATT-10-PER-COL"
    mapping = [6,7,4,5,2,3,0,1]
    initial_amp = [3,23,43,63,63,43,23,3]
    initial_phases = [0x00 for i in range(0,len(mapping))]
    phase_increment = 11.25/2
    phase_shifts = np.arange(0, 360, phase_increment)
    phase_states_to_meas = np.zeros((len(mapping),len(phase_shifts)))
    phase_states_to_meas_disc = np.zeros((len(mapping),len(phase_shifts)),dtype=int)
    #Add to inital state the sequence of phase shifting
    for i in range(0,len(mapping)):
        phase_states_to_meas[i,:] = np.mod(initial_phases[i]+phase_shifts,360)
    phase_states_to_meas_disc = (phase_states_to_meas/phase_increment).astype(int)

    #Start Connection with the VNA
    pna = N5264A(addr=pna_ip_addr)
    pna.preset()
    pna.setup_single_freq_cut(28,len(phase_shifts))
    pna.config_manual_trigger()

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
    measured_data = np.zeros((len(mapping), len(phase_shifts)), dtype=complex)

    #Measure Phase shift
    for j in range(0,len(mapping)):
        for i in range(0,len(phase_shifts)):
            board.send_set_phase_amp_to_channel(mapping[j],phase_states_to_meas_disc[j,i],initial_amp[j])
            pna.send_trigger()
        meas_trace = np.array(pna.get_data_double(),dtype=complex)
        measured_data[j,:] = meas_trace[::2]+1j*meas_trace[1::2]
            

    recovered_excitation = np.zeros(len(mapping), dtype=complex)
    for i in range(0, len(mapping)):
        recovered_excitation[i] = calc(measured_data[i,:],phase_shifts)
        plt.plot(phase_shifts, 20 * np.log10(np.abs(measured_data[i, :])))
        print(f"E{i+1} Amp:{np.abs(recovered_excitation[i]/recovered_excitation[0]):2.2f}"
              f" Phase:{np.rad2deg(np.angle(recovered_excitation[i]/recovered_excitation[0])):2.2f}")
    plt.show()
    scipy.io.savemat(f"{outfile}.mat",{"meas_rev": measured_data,"cal_coefs":recovered_excitation})


def main_simulation ():
    eng = matlab.engine.start_matlab()
    eng.cd(r'HertzDipole', nargout=0)
    xp = np.linspace(-1.75, 1.75, 8)
    yp = xp * 0
    zp = xp * 0
    ai = np.ones(len(xp))
    Theta = 0.0
    Phi = 0.0
    kr = 5 / (3e8 / 28e9)

    # Aim the array
    ai = ai * np.exp(1j * np.deg2rad(np.linspace(0, 355, 8)))

    phase_shift = np.arange(0, 360, 1)
    measured_data = np.zeros((len(xp), len(phase_shift)), dtype=complex)

    for i in range(0, len(xp)):
        for j in range(0, len(phase_shift)):
            shifted_ai = np.copy(ai)
            shifted_ai[i] = shifted_ai[i] * np.exp(1j * np.deg2rad(phase_shift[j]),dtype=complex)
            _, _, _, measured_data[i, j], _ = eng.dipoleXArray(xp, yp, zp, shifted_ai, Theta, Phi, kr, nargout=5)

    recovered_excitation = np.zeros(len(xp), dtype=complex)
    for i in range(0, len(xp)):
        recovered_excitation[i] = calc(measured_data[i,:],phase_shift)
        plt.plot(phase_shift, 20 * np.log10(np.abs(measured_data[i, :])))
        print(f"E{i+1} Amp:{np.abs(recovered_excitation[i]/recovered_excitation[0]):2.2f}"
              f" Phase:{np.rad2deg(np.angle(recovered_excitation[i]/recovered_excitation[0])):2.2f}")
    plt.show()




if __name__ == "__main__":
    main_measurement()
