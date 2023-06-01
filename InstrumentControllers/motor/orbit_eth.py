import pyvisa
import time

from loguru import logger

class Orbit:
    __instance = None
    _connection_open = False
    _visa = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if Orbit.__instance == None:
            Orbit()
        return Orbit.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if Orbit.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Orbit.__instance = self

    def open_connection(self,addr="TCPIP0::172.17.1.33::1234::SOCKET"):
        if not self._connection_open:
            try:
                self._visa = pyvisa.ResourceManager().open_resource(
                    addr, query_delay=0.1)
                self._visa.write_termination = "\r\n"
                self._visa.timeout = 1000
                self._connection_open = True
                self._visa.flush(pyvisa.constants.VI_READ_BUF_DISCARD |
                                 pyvisa.constants.VI_WRITE_BUF_DISCARD)
                self._visa.clear()  # Need 1s delay to clear buffers
                time.sleep(1)
            except Exception as exp:
                self.close_connection()
                logger.error(exp)
                logger.error("Error openning Visa")
                raise Exception("Connection Already Openned")

    def close_connection(self):
        if self._connection_open:
            try:
                #self._write_instrument("H")
                self._visa.close()
                self._connection_open = False
            except:
                logger.error("Error Closing VISA")

    def _write_instrument(self, query, delay=0.1):
        self._visa.write(query)
        logger.debug(query)
        time.sleep(delay)

    def _read_instrument(self, query, delay=0.1):
        read = str(self._visa.query(query))
        logger.debug(query+" --> "+read)
        time.sleep(delay)
        return read

    def _read_status_byte(self):
        last_wl = self._visa.write_termination
        last_rl = self._visa.read_termination
        self._visa.write_termination = "\n"
        self._visa.read_termination = "\n"
        stb = self._visa.query("++spoll")
        self._visa.write_termination = last_wl
        self._visa.read_termination = last_rl

        return int(stb[0:2])

    def _offset_parser(self, offset):
        return float(offset[1:len(offset)-4] + "." + offset[len(offset)-4:len(offset)-2])

    def read_offset(self, axis):
        if (axis <= 0 or axis > 6):
            logger.err("Error: (ReadOffset) axis is not ok AX:" + str(axis))
            return
        self.open_connection()
        self._write_instrument("H")
        self._write_instrument("S")
        try:
            read_offset = self._read_instrument("A{}<O<".format(axis))
            self.close_connection()
        except:
            logger.error("Orbit error with offset: {}".format(self._visa.stb))
            self.close_connection()
            raise Exception("ERROR READING")
        logger.info("Read Offset from AX:" + str(axis) + "O:" + read_offset)
        # Format is Sxxxyy xxx integer part yy decimal part
        return self._offset_parser(read_offset)

    def read_all_offsets(self, n_ax=6):
        offsets = []
        self.open_connection()
        self._write_instrument("H")
        self._write_instrument("S")
        for i in range(1, n_ax+1):
            self._write_instrument("A{}<".format(i), delay=1)
            offsets.append(self._offset_parser(
                self._read_instrument("O<")))
        self.close_connection()
        return offsets

    def write_offset(self, axis, offset):
        if (axis <= 0 or axis > 6):
            logger.error("Error: (WriteOffset) axis is not ok AX:" +
                  str(axis) + " O:" + str(offset))
            return
        elif (offset < 0 or offset >= 360):
            logger.error("Error: (WriteOffset) offset is not ok AX:" +
                  str(axis) + " O:" + str(offset))
            return

        self.open_connection()
        self._write_instrument("L")
        self._write_instrument("A{}<".format(axis))
        self._write_instrument(
            "O"+"".join("{:06.2f}".format(offset).split(".")) + "<")
        self._write_instrument("H")
        # Save to permanent Memory
        self._write_instrument("K<",delay=0.5)
        self.close_connection()

        # Check Offset written
        new_offset = self.read_offset(axis)
        if(new_offset != offset):
            raise Exception("Offset written not stored")
        return new_offset

    def _position_parser(self, position):
        pos = float(position[5:len(position)-5]+"."+position[-5:-3])
        ax = int(position[3])
        return (ax, pos)

    def read_position(self, axis):
        if (axis <= 0 or axis > 6):
            logger.error("Error: (WriteOffset) axis is not ok AX:" + str(axis))

        self.open_connection()
        self._write_instrument("E{}<".format(axis),delay=1)
        try:
            res = self._position_parser(self._read_instrument("X2<"))
        except:
            logger.error("Error reading position STB:{}".format(self._visa.stb))
            self.close_connection()
            raise Exception("ERROR READING")
        if (res[0] != axis):
            self.close_connection()
            raise Exception("Axis not matching")
        self.close_connection()
        return res[1]

    def read_all_positions(self, n_ax=6):
        positions = []
        self.open_connection()
        for i in range(1, n_ax+1):
            self._write_instrument("E{}<".format(i), delay=1)
            try:
                position = self._position_parser(
                    self._read_instrument("X2<"))
            except:
                self.close_connection()
                raise
            if position[0] != i:
                self.close_connection()
                raise Exception("Axis not matching")    
            positions.append(position[1])
        self.close_connection()
        return positions

    def mode_register_movement(self, axis, pos_origin, pos_end, speed, angular_increment,direction):
        self.open_connection()
        self._write_instrument("L")
        self._write_instrument("Da"+direction+"<")
        self._write_instrument("Aa{}<".format(axis))
        self._write_instrument(
            "Pas"+"".join("{:06.2f}".format(pos_origin).split("."))+"<")
        self._write_instrument(
            "Pab"+"".join("{:06.2f}".format(pos_end).split("."))+"<")
        self._write_instrument(
            "Va"+"".join("{:06.1f}".format(speed).split("."))+"<")
        self._write_instrument(
            "I"+"".join("{:06.3f}".format(angular_increment).split("."))+"<")
        self._write_instrument("MR")
        self._write_instrument("H")
        self._write_instrument("G")
        start_time = time.time()
        while(True):
            if(self._read_status_byte() == 88):
                break
            elif time.time() - start_time >= 600:
                self.close_connection()
                raise Exception("Timeout")
            time.sleep(0.4)
        self.close_connection()

    def mode_position_movement(self, axis, pos_target, direction, speed):
        self.open_connection()
        self._write_instrument("H")
        self._write_instrument("L")
        self._write_instrument("Aa{}<".format(axis))
        self._write_instrument("Pat"+"".join("{:06.2f}".format(pos_target).split("."))+"<")
        self._write_instrument("Da"+direction+"<")
        self._write_instrument("Va"+"".join("{:06.1f}".format(speed).split("."))+"<")
        self._write_instrument("MT")
        self._write_instrument("H")
        self._write_instrument("G") #delay included in write instrument
        start_time = time.time()
        while(True):
            if(self._read_status_byte() == 88):
                break
            elif time.time() - start_time >= 600:
                self.close_connection()
                raise Exception("Timeout, prob end missed")
            time.sleep(0.1)
        self.close_connection()

    
    def read_limit(self,axis):
        limit = {"number":axis}
        self.open_connection()
        self._write_instrument("H")
        self._write_instrument("S")
        limit["forwardLimit"] = self._offset_parser(self._read_instrument("A{}<Bf<".format(axis)));
        limit["reverseLimit"] = self._offset_parser(self._read_instrument("A{}<Br<".format(axis)));
        self._write_instrument("H")
        self.close_connection()
        return limit

    def read_limits(self,n_ax=6):
        limits = []
        for i in range(1,n_ax+1):
            limits.append(self.read_limit(i))
        return limits
    
    def write_limit(self,axis,lim_fwd,lim_rev):
        self.open_connection()
        self._write_instrument("H")
        self._write_instrument("L")
        self._write_instrument("A{}<".format(axis)+"Bf"+"".join("{:06.2f}".format(lim_fwd).split(".")) + "<");
        self._write_instrument("A{}<".format(axis)+"Br"+"".join("{:06.2f}".format(lim_rev).split(".")) + "<");
        self.close_connection()

    def tester(self):
        logger.debug("Working Instrument")

if __name__ == "__main__":
    orbit = Orbit.get_instance()
    orbit.mode_register_movement(5,330.24,360.24,90,0.5,"f")
    orbit.mode_register_movement(5,360.23,330.24,90,0.5,"r")
    orbit.mode_register_movement(5,330.24,360.24,90,0.5,"f")