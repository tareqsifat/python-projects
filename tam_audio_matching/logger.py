import logging
from datetime import datetime

class Logger:
    def __init__(self):
        # Create and configure logger
        logging.basicConfig(filename=f"{datetime.now()}.log",
                            format='%(asctime)s %(message)s',
                            filemode='w')
        # Creating an object
        self.logger = logging.getLogger()
        # Setting the threshold of logger to DEBUG
        self.logger.setLevel(logging.DEBUG)

    def get_logger(self):
         return self.logger
