import logging
import sys
from datetime import date
from datetime import datetime
import coloredlogs

_logger = logging.getLogger('mopshub_log')
_logger.setLevel(logging.WARNING)
# coloredlogs.install(level='DEBUG', logger=_logger)

now = datetime.now()
current_time = now.strftime("%H-%M-%S")

fh = logging.FileHandler(f'log/mopshub_log_Date-{date.today()}_Time-{current_time}', 'w')
fh.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

ch = logging.StreamHandler()
ch.setStream(sys.stdout)
ch.setLevel(logging.WARNING)

_logger.addHandler(fh)
_logger.addHandler(ch)