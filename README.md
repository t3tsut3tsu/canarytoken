[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/t3tsut3tsu/canarytoken/blob/master/README.md)
[![ru](https://img.shields.io/badge/lang-ru-green.svg)](https://github.com/t3tsut3tsu/canarytoken/blob/master/README.ru.md)

# Canarytoken

## Quick installation

1. Clone the repo: 

   ```git clone https://github.com/t3tsut3tsu/canarytoken```
2. Move to the directory:
   
   ```cd canarytoken/```
4. Install dependencies:
   
   ```pip install -r requirements.txt```
6. Run:
   
   ```python main.py <>```

## Program specification
...

## Operating modes

### attack
- Starts the listener and initializes sending emails to a list of addresses.

### listener
- Starts a listener to receive incoming connections.

### send
- Initializes sending emails to a list of addresses.

### static
- Creates a token on the hard disk.

### report
- Generates a launch report based on data from the database.

### merge
- Connects two databases for further generation of a common report, creates a backup copy of the first database.
