import logging
import os

def logger():
    os.makedirs('logs', exist_ok=True)

    logging.basicConfig(
        filename='logs/logfile.txt',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)

logger()