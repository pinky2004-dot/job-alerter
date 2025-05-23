#keeps track of what's happening, and if there are errors and success messages
import logging

# Set up logger
logger = logging.getLogger('job-alerter')
logger.setLevel(logging.INFO)

# Create console handler and set level to info
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

# Add handler to logger
logger.addHandler(ch)

# Optionally: I could add file logging if I wanted logs saved in a file.
# fh = logging.FileHandler('job-scout.log')
# fh.setFormatter(formatter)
# logger.addHandler(fh)