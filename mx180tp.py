"""Manage MX180TP"""

import logging
import argparse
import socket
import time

logger = logging.getLogger(__name__)

class MX180TP:
    """MX180TP class"""

    def __init__(self, ip: str, port: int = 9221, connect: bool = True) -> None:
        """Initialize a new instance of the class

        Args:
            ip (str): _description_
            port (int, optional): _description_. Defaults to 9221.
            connect (bool, optional): _description_. Defaults to True.
        """
        self.ip = ip
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(3.0)

        if connect:
            self.connect()

    def connect(self) -> None:
        """Connect"""
        try:
            self.s.connect((self.ip, self.port))
        except Exception as e:
            logging.error(f"Exception '{e}' while connecting to{self.ip}:{self.port}")
            raise Exception(f"Exception '{e}' while connecting to{self.ip}:{self.port}")

    def __send_req(self, cmd: str) -> str:
        self.s.send(cmd.encode())
        try:
            data = self.s.recv(1024).decode()
        except Exception:
            logging.error("Error: no data recv")
            return "Error: no data recv"
        return data.strip()

    def __send_cmd(self, cmd: str) -> None:
        self.s.send(cmd.encode())
        time.sleep(1)

    def get_ip(self) -> str:
        """Return IP"""
        return self.ip

    def get_port(self) -> int:
        """Return port"""
        return self.port

    def get_name(self) -> str:
        """Send *IDN? command

        Returns the instrument identification.
        The exact response is determined by the instrument configuration and is of the form: <NAME>,<model>, <serial no.>, <version>
        where
        <NAME> is the manufacturer's name,
        <model> defines the type of instrument,
        <serial> is the unit serial number and
        <version> is the revision level of the software installed.
        """
        string = "*IDN?\n"
        return self.__send_req(string)

    def get_set_current(self, channel: int) -> str:
        """Send I<n>?

        Return the set current of output <n>.
        Response is I<n> <nr2>,
        where <nr2> is in amps.

        Args:
            channel (int): n

        Returns:
            str: nr2
        """
        string = f"I{channel}?\n"
        return self.__send_req(string)

    def get_set_voltage(self, channel: int) -> str:
        """Send V<n>?

        Return the set voltage of output <n>.
        Response is V<n> <nr2>,
        where <nr2> is in volts.

        Args:
            channel (int): n
        Returns:
            str: nr2
        """
        string = f"V{channel}?"
        return self.__send_req(string)

    def get_output_current(self, channel: int) -> str:
        """Send I<n>?

        Return the set current of output <n>. Response is I<n> <nr2>,
        where <nr2> is in amps.

        Args:
            channel (int): n
        Returns:
            str: nr2
        """
        string = f"I{channel}O?"
        return self.__send_req(string)

    def get_output_state(self, channel: int) -> str:
        """Send OP<n>?

        Returns output <n> on or off status.
        Response <nr1> has the following meaning: 1 = ON, 0 = OFF

        Args:
            channel (int): n
        Returns:
            str: nr2
        """
        string = f"OP{channel}?"
        return self.__send_req(string)

    def get_output_voltage(self, channel: int) -> str:
        """Send V<n>O?

        Return output <n> measured voltage.
        Response is <nr2>V,
        where <nr2> is in volts.

        Args:
            channel (int): n
        Returns:
            str: nr2
        """
        string = f"V{channel}O?"
        return self.__send_req(string)

    def set_output_state(self, channel: int, state: bool) -> None:
        """Send OP<n> <nrf>

        Set output <n> on or off, where <nrf> has the following meaning: 1 = ON, 0 = OFF.

        Args:
            channel (int): n
            state (bool): nrf
        """
        status_int = int(state)
        string = f"OP{channel} {status_int}"
        self.__send_cmd(string)

    def set_voltage(self, channel: int, voltage: float) -> None:
        """Send V<n> <nrf>

        Set output <n> to <nrf> volts.

        Args:
            channel (int): n
            voltage (float): nrf
        """
        string = f"V{channel} {voltage}"
        self.__send_cmd(string)

    def set_current(self, channel: int, current: float) -> None:
        """Send I<n> <nrf>

        Set the output <n> current limit to <nrf>.

        Args:
            channel (int): n
            current (float): nrf
        """
        string = f"I{channel} {current}"
        self.__send_cmd(string)

    def set_output_state_all(self, state: bool) -> None:
        """Send OPALL <nrf>

         Set all outputs on or off,
         where <nrf> has the following meaning: 1 = ON, 0 = OFF
         NOTE: when using "set_output_state_all" the status of the channels won't be available (always 0)

        Args:
            state (bool): nrf
        """
        status_int = int(state)
        string = f"OPALL {status_int}"
        self.__send_cmd(string)

    def turn_on_channel(self, channel: str) -> None:
        """
        Turns on a channel, verifying it is on or retrying up to 4 times.

        Args:
            channel (int): channel to be turned on [1,2,3].
        """
        if channel not in range(1, 4):
            logging.error(f"Channel {channel} not supported")
            return
        for i in range(1, 5):
            if self.get_output_state(channel) == "1":
                logging.info(f"{self.ip} Channel {channel} turned on in {i} retries")
                return
            self.set_output_state(channel, True)
        logging.error(f"{self.ip} Error: could not turn on channel {channel} after {i} retries")

    def turn_off_channel(self, channel: str) -> None:
        """Turns off a channel, verifying it is off or retrying up to 4 times.

        Args:
            channel (int): channel to be turned off [1,2,3].
        """
        if channel not in range(1, 4):
            logging.error(f"Channel {channel} not supported")
            return
        for i in range(1, 5):
            if self.get_output_state(channel) == "0":
                logging.info(f"{self.ip} Channel {channel} turned off in {i} retries")
                return
            self.set_output_state(channel, False)
        logging.error(f"{self.ip} Error: could not turn off channel {channel} after {i} retries")

    def show_data(self) -> str:
        """Returns a string describing device name, connection parameters and status, ready to be printed."""
        out_str = ""

        name = self.get_name()
        ip = self.get_ip()
        port = self.get_port()
        out_str += f"IP: {ip}:{port} \tName: {name} \n"

        for i in range(1, 4):
            s1 = self.get_output_state(i)
            i1 = self.get_output_current(i)
            v1 = self.get_output_voltage(i)
            out_str += f"CH{i} \t\t St:{s1},\tV:{v1},\tI:{i1} \n"

        return out_str


def main() -> int:
    """Main entry point"""
    # usage: mx180tp.py [-h] [-p PORT] ip [{status,ON,OFF}] [channel] [value]

    parser = argparse.ArgumentParser(description="Control TTi MX180TP over TCP")
    parser.add_argument("ip", help="IP address")
    parser.add_argument("-p", "--port", action="store", dest="port", help="TCP Port on device", default=9221)
    parser.add_argument("command", nargs="?", choices=["status", "on", "off", "set_voltage"], help="Command to be executed:")
    parser.add_argument("channel", nargs="?", type=int, help="channel", default=-1)
    parser.add_argument("value", nargs="?", type=float, help="value", default=0.0)

    args = parser.parse_args()

    if None in [args.ip, args.command]:
        print("Missing arguments")
        return 1

    ps = MX180TP(args.ip, args.port)

    if args.command == "status":
        print(ps.show_data())

    if args.command in ["ON", "on", "On"]:
        if args.channel == -1:
            ps.set_output_state_all(True)
        elif args.channel in range(1, 3):
            ps.turn_on_channel(args.channel)

    if args.command in ["OFF", "off", "Off"]:
        if args.channel == -1:
            ps.set_output_state_all(False)
        elif args.channel in range(1, 3):
            ps.turn_off_channel(args.channel)

    if args.command == "set_voltage":
        if args.channel in range(1, 3) and args.value != 0.0:
            ps.set_voltage(args.channel, args.value)

    return 0


if __name__ == "__main__":
    main()
