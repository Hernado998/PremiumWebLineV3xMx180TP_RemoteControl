"""Class of the EGPM2"""

import argparse
import re
import subprocess
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class EGPM2:
    """Class of the EGPM2"""

    def __init__(self, ip: str, port: int = 80, connect: bool = True, password: str = "1") -> None:
        """Initialize a new instance of the class

        Args:
            ip (str): _description_
            port (int, optional): _description_. Defaults to 80.
            connect (bool, optional): _description_. Defaults to True.
            password (str, optional): _description_. Defaults to "1".
        """
        self.ip = ip
        self.port = port
        self.password = password
        self.ch_state = []
        self.mac = ""
        if connect:
            self.connect()

    def __run_command(self, cmd: str):
        """Runs a shell command.

        Args:
            cmd (str): command to be run
            stdout (bool, optional): If true, the function returns the output of the command. Defaults to False.

        Returns:
            int: if stdout is true, returns the output of the command
        """
        sp = subprocess.run(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        return sp.stdout

    def connect(self) -> None:
        """Connect"""
        try:
            cmd = f"wget http://{self.ip}:{self.port}/login.html --post-data=pw={self.password} -O -"
            self.__run_command(cmd)
        except Exception as e:
            logging.error(f"Exception '{e}' while connecting to{self.ip}:{self.port}")

    def get_ip(self) -> str:
        """Return IP"""
        return self.ip

    def get_port(self) -> int:
        """Return port"""
        return self.port

    def get_name(self) -> str:
        """Return name"""
        return f"EGPM2 @ {self.ip}"

    def __get_data(self) -> None:
        """Gets data from the web interface of the powerstrip.

        Just uses a wget and extract from the reply the status of the sockets and the mac address.
        """
        try:
            cmd = f"wget http://{self.ip}:{self.port}/ -O -"
            output = str(self.__run_command(cmd))
            if "sockstates = " in output:
                start = output.index("sockstates = [") + len("sockstates = [")
                end = start + len("0,0,0,0")
                self.ch_state = output[start:end].split(",")

            else:
                logging.error("Error, sockstates not found in: \n" + output)

            if 'mac= "' in output:
                start = output.index('mac= "') + len('mac= "')
                end = start + len("AABBCCEEDDFF")
                self.mac = output[start:end]
            else:
                logging.error("Error, mac not found in: \n" + output)

        except Exception as e:
            logging.error(f"Exception '{e}' while collecting info")

    def get_output_state(self, socket_id: int) -> str:
        """Return output state"""
        try:
            cmd = f"wget http://{self.ip}:{self.port}/ -O -"
            html = self.__run_command(cmd)
            html_string = html.decode("utf-8")

            soup = BeautifulSoup(html_string, "html.parser")

            res = soup.findAll("script")[0]

            return re.search(r"var sockstates = (.*?);", str(res)).group(1)[1:-1].split(",")[socket_id - 1]

        except Exception as e:
            logging.error(f"Exception '{e}' while collecting info")

    def set_output_state(self, channel: int, state: bool) -> None:
        """Set output <channel (1-4)> ON or OFF"""
        try:
            state_int = int(state)
            cmd = f"wget http://{self.ip}:{self.port}/ --post-data=cte{channel}={state_int} -O -"
            self.__run_command(cmd)
        except Exception as e:
            logging.error(f"Exception '{e}' while switching output {channel}")

    def show_data(self) -> str:
        """Returns a string describing device name, connection parameters and status, ready to be printed."""
        self.__get_data()
        return f"EGPM2 Power strip \nIP: {self.ip} PORT:{self.port} MAC: {self.mac} \nChannels status: {self.ch_state} "

    def set_output_state_all(self, state: bool) -> None:
        """Set all outputs on or off,

        Args:
            state (bool): target state (on/off)
        """
        for i in range(1, 5):
            self.set_output_state(i, state)

    def turn_on_channel(self, channel: int) -> None:
        """Turns on a channel, verifying it is on or retrying up to 4 times.

        Args:
            channel (int): channel to be turned on [1,2,3,4].
        """
        if channel not in range(1, 5):
            logging.warn(f"Channel {channel} not supported")
            return
        self.set_output_state(channel, True)
        self.__get_data()

        if self.ch_state[channel - 1] == "1":
            logging.info(f"Turned on channel {channel}")
        else:
            logging.error(f"Error turning on channel {channel}")

    def turn_off_channel(self, channel: int) -> None:
        """Turns off a channel, verifying it is off or retrying up to 4 times.

        Args:
            channel (int): channel to be turned off [1,2,3,4].
        """
        if channel not in range(1, 5):
            logging.warn(f"Channel {channel} not supported")
            return
        self.set_output_state(channel, False)
        self.__get_data()

        if self.ch_state[channel - 1] == "0":
            logging.info(f"Turned off channel {channel}")
        else:
            logging.error(f"Error turning off channel {channel}")


def main() -> int:
    """Main entry point"""
    # usage: EGPM2_HTTP.py [-h] [-p PORT] ip [{ON,OFF}] [channel]

    parser = argparse.ArgumentParser(description="Control Energenie EGPM2 power strip over HTTP")
    parser.add_argument("ip", help="IP address")
    parser.add_argument(
        "-p",
        "--port",
        action="store",
        dest="port",
        help="TCP Port on device",
        default=80,
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=["status", "on", "off"],
        help="Command to be executed:",
    )
    parser.add_argument("channel", nargs="?", type=int, help="channel", default=-1)

    args = parser.parse_args()

    if None in [args.ip, args.command]:
        print("Missing arguments")
        return 1

    ps = EGPM2(args.ip, args.port)

    if args.command == "status":
        print(ps.show_data())

    if args.command in ["ON", "on", "On"]:
        if int(args.channel) in range(1, 5):
            ps.set_output_state(args.channel, True)
        else:
            print(f"Channel {args.channel} not supported for command {args.command}")

    if args.command in ["OFF", "off", "Off"]:
        if int(args.channel) in range(1, 5):
            ps.set_output_state(args.channel, False)
        else:
            print(f"Channel {args.channel} not supported for command {args.command}")

    return 0


if __name__ == "__main__":
    main()
