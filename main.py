# main.py
import mx180tp
import webline
import energeniepm
import datetime
import logging
import logging.config
import os
import signal

def power_off():
    try :
        logging.info("Powering off ...")
        wl = webline.WEBLINE("10.152.4.143", "admin", "admin", 0)
        eg = energeniepm.EGPM2("10.152.4.191")
        wl.turn_off()
        eg.turn_off_channel(3)

        mx_154 = mx180tp.MX180TP("10.152.4.154", 9221)
        mx_154.turn_off_channel(1)
        mx_157 = mx180tp.MX180TP("10.152.4.157", 9221)
        mx_157.turn_off_channel(1)
        mx_157.turn_off_channel(2)
    except Exception as e:
        logging.error(f"Exception '{e}' while powering off")

def power_on():
    try:
        logging.info("Powering on ...")
        wl = webline.WEBLINE("10.152.4.143", "admin", "admin", 0)
        eg = energeniepm.EGPM2("10.152.4.191")
        wl.turn_on()
        eg.turn_on_channel(3)

        mx_154 = mx180tp.MX180TP("10.152.4.154", 9221)
        mx_154.turn_on_channel(1)
        mx_157 = mx180tp.MX180TP("10.152.4.157", 9221)
        mx_157.turn_on_channel(1)
        mx_157.turn_on_channel(2)
    except Exception as e:
        logging.error(f"Exception '{e}' while powering on")

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
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': log_path,
                'formatter': 'default',
            },
        },
        'root': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
    }

    # Apply the logging configuration
    logging.config.dictConfig(logging_config)

    # Example usage of the logger in the main module
    logger = logging.getLogger(__name__)
    logger.info("Logging is configured and ready.")

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    logging.info("Starting process ...")
    while(True):
        now = datetime.datetime.now()

        current_hour = now.hour
        current_minute = now.minute

        if (((current_hour == 18 and current_minute == 0) or (days[now.weekday()] in ["Saturday", "Sunday"])) and flag == True):
            power_off()
            flag = False

        if current_hour == 8 and current_minute == 0 and days[now.weekday()] in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"] and flag == False:
            power_on()
            flag = True


if __name__ == "__main__":
    main()
