# main.py
import mx180tp
import webline
import datetime
import logging
import os
import signal

# Initialize the flag globally
flag = True

def power_off():
    logging.info("Powering off ...")
    wl = webline.WEBLINE("10.152.4.143", "admin", "admin", 0)
    wl.turn_off()

    mx_154 = mx180tp.MX180TP("10.152.4.154", 9221)
    mx_154.turn_off_channel(1)
    mx_157 = mx180tp.MX180TP("10.152.4.157", 9221)
    mx_157.turn_off_channel(1)
    mx_157.turn_off_channel(2)

def power_on():
    logging.info("Powering on ...")
    wl = webline.WEBLINE("10.152.4.143", "admin", "admin", 0)
    wl.turn_on()

    mx_154 = mx180tp.MX180TP("10.152.4.154", 9221)
    mx_154.turn_on_channel(1)
    mx_157 = mx180tp.MX180TP("10.152.4.157", 9221)
    mx_157.turn_on_channel(1)
    mx_157.turn_on_channel(2)

def signal_handler(sig, frame):
    if sig == signal.SIGUSR1:
        logging.warning(f"Detected signal {signal.SIGUSR1}")
        power_off()
    if sig == signal.SIGUSR2:
        logging.warning(f"Detected signal {signal.SIGUSR2}")
        power_on()

def main():

    flag = True

    signal.signal(signal.SIGUSR1, signal_handler)
    signal.signal(signal.SIGUSR2, signal_handler)

    # Define the path where the log file will be saved
    log_directory = "/power_app/logs"
    log_filename = "power_app.log"
    log_path = os.path.join(log_directory, log_filename)

    # Create the log directory if it doesn't exist
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    # Configure the logging settings
    logging.basicConfig(
        level=logging.DEBUG,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format="%(asctime)s - %(levelname)s - %(message)s",  # Define the format of log messages
        handlers=[
            logging.FileHandler(log_path),  # Save log messages to the specified file
            logging.StreamHandler()  # Optionally, print log messages to the console
        ]
    )

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    logging.info("Starting process ...")
    while(True):
        now = datetime.datetime.now()

        current_hour = now.hour
        current_minute = now.minute

        if (((current_hour == 18 and current_minute == 0) or (days[now.weekday()] in ["Saturday", "Sunday"])) and flag == True):
            power_off()
            flag = False

        if current_hour == 8 and current_minute == 30 and days[now.weekday()] in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"] and flag == False:
            power_on()
            flag = True


if __name__ == "__main__":
    main()
