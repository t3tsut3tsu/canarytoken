import logging

def logger():
    logging.basicConfig(
        filename='logs/logfile.txt',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logger()