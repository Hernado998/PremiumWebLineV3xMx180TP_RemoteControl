# Brennenstuhl Premium-Web-Line V3 is a socket strip with an embedded web server.
# It can be switched via a web interface or using http get requests. The latter is a bit under-documented,
# so here's what i found out:
# The built-in server accepts only authenticated http get requests (using digest auth).
# each command has its own url, like so: http://{IP-OF-THE-SOCKETSTRIP}/cgi/{commandname}?params
# full list can be found in a PDF called "Premium-Web-Line V3 CGI specification.pdf" which is included in the download package of the official software:
# download link -> https://www.brennenstuhl.com/index.php?module=explorer&index[explorer][action]=download&index[explorer][file]=firmware/premium-web-line-v3-software-3_3_6.zip

# here's an example on how to toggle one of the two relais (nr. 0)
# modified a general digest auth example from stackoverflow: https://stackoverflow.com/questions/23254013/http-digest-basic-auth-with-python-requests-module


import logging
import requests
from requests.auth import HTTPDigestAuth
import argparse

try:
    import httplib
except ImportError:
    import http.client as httplib

class WEBLINE:

    """
    Initialize the WEBLINE object with the provided IP address, username, password, and optional port.

    Args:
        ip (str): The IP address of the WEBLINE.
        user (str): The username for authentication.
        password (str): The password for authentication.
        port (int, optional): The port number for the WEBLINE. Defaults to 0.

    Returns:
            None
    """
    def __init__(self, ip: str, user: str = 'admin', password: str = 'admin', port: int = 0) -> None:
        self.user = user
        self.password = password
        self.ip = ip
        self.port = port

    def turn_off(self):
        httplib.HTTPConnection.debuglevel = 1

        logging.basicConfig(level=logging.INFO)
        url = f'http://{self.ip}/cgi/relaySt?Rel={self.port}'
        r = requests.get(url, auth=HTTPDigestAuth(self.user, self.password),
                        timeout=10)

        if(r.text == 'on'):
            logging.info("Turning off Webline ...")
            url = f'http://{self.ip}/cgi/toggleRelay?Rel={self.port}'
            r = requests.get(url, auth=HTTPDigestAuth(self.user, self.password),
                                timeout=10)
        elif(r.text == 'off'):
            logging.error("Webline is already off")

    def turn_on(self):
        httplib.HTTPConnection.debuglevel = 1

        logging.basicConfig(level=logging.INFO)
        url = f'http://{self.ip}/cgi/relaySt?Rel={self.port}'
        r = requests.get(url, auth=HTTPDigestAuth(self.user, self.password),
                        timeout=10)

        if(r.text == 'off'):
            logging.info("Turning on Webline ...")
            url = f'http://{self.ip}/cgi/toggleRelay?Rel={self.port}'
            r = requests.get(url, auth=HTTPDigestAuth(self.user, self.password),
                                timeout=10)
        elif(r.text == 'on'):
            logging.error("Webline is already on")


def main() -> int:
    """Main entry point"""

    parser = argparse.ArgumentParser(description="Control Brennenstuhl Premium-Web-Line V3 over TCP")
    parser.add_argument("ip", help="IP address")
    parser.add_argument("-u", "--user", action="store", dest="user", help="Username", default="admin")
    parser.add_argument("-w", "--password", action="store", dest="password", help="Password", default="admin")
    parser.add_argument("-p", "--port", action="store", dest="port", help="TCP Port on device", default=0)
    parser.add_argument("command", choices=["on", "off"], help="Command to be executed:")

    args = parser.parse_args()

    if None in [args.ip]:
        print("Missing arguments")
        return 1

    ps = WEBLINE(args.ip, args.user, args.password, args.port)

    ps.turn_on()
    #ps.turn_off()

    return 0


if __name__ == "__main__":
    main()
