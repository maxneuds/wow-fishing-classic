import logging
from datetime import datetime as dt

# define a custom formatter
class CustomFormatter(logging.Formatter):
    def format(self, record):
        # get name of current running function
        record.function_name = record.funcName
        return super().format(record)

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create stream handler
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

# setup the custom formatter
# formatter = CustomFormatter('[%(asctime)-s] [%(levelname)-5s] [%(filename)s:%(lineno)d]  %(message)-s', datefmt='%Y/%m/%d %H:%M:%S')
formatter = CustomFormatter('[%(asctime)-s] [%(levelname)-5s] [%(filename)s:%(lineno)d]  %(message)-s', datefmt="%H:%M:%S")
handler.setFormatter(formatter)

# add handler to logger
logger.addHandler(handler)

# custom logging functions
def log_exetime(t0: dt):
    """
    log execution time, given a starting time t0 (datetime.datetime)
    """
    runtime = dt.now() - t0
    seconds = runtime.total_seconds()
    logger.debug(f"Execution time: {seconds:.0f}s")
